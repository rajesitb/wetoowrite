import json
import boto3
from botocore.client import Config
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
import tweepy as tw
from django.views import View

from textblob import TextBlob
import textwrap
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from tracking_analyzer.models import Tracker
from django.utils.text import slugify

from .forms import PostForm, CommentsForm, CommentReplyForm, TrendsForm, get_trends, \
    TwitterSearchForm, PhotoForm, PhotoStoryForm
from .models import Post, Comments, CommentReply, Contact, Action, Photo, PhotoStory
from .utils import summary, create_action, tag_list
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)
import os
from better_profanity import profanity
from textblob import TextBlob


def search_blog(query=None):
    queryset = []
    queries = query.split(' ')
    for q in queries:
        posts = Post.objects.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q))
        for post in posts:
            queryset.append(post)
    return list(set(queryset))


def search_view(request):
    context = {}
    query = ''
    if request.GET:
        query = request.GET['q']
        context['query'] = str(query)
    blog_posts = search_blog(query)
    context['object_list'] = blog_posts
    return render(request, 'blog/search.html', context)


def about(request):
    return render(request, 'blog/about.html')


def privacy(request):
    return render(request, 'blog/privacy.html')


def tnc(request):
    return render(request, 'blog/tnc.html')


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'object_list'
    paginate_by = 4

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['pk'])
        # first_name = self.kwargs.get('username').split(' ')[0]
        # try:
        #     user = User.objects.get(first_name=first_name)
        # except (User.DoesNotExist, MultipleObjectsReturned):
        #     user = User.objects.get(username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).filter(draft=False).order_by('-publish')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs['pk'])
        # user_ref = self.request.build_absolute_uri()
        # user_list = list(user_ref.split('/'))
        # user_name = user_list[len(user_list) - 2]
        # first_name = user_name.split('%')[0]
        # try:
        #     first_name = User.objects.get(first_name=first_name).get_full_name()
        # except User.DoesNotExist:
        #     first_name = User.objects.get(username=self.kwargs['username']).get_full_name()
        context['user_post'] = user.get_full_name()
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        title = form.cleaned_data['title']
        title = form.cleaned_data['is_draft']
        form.instance.slug = slugify(title)
        # post needs to be vetted by the admin before making it public
        form.instance.draft = True
        # post = Post.objects.latest('publish')
        new_post = form.save(commit=False)
        new_post.save()
        followers = new_post.author.rel_to_set.all()
        emails = ['from.wetoowrite@gmail.com', ]

        for follower in followers:
            emails.append(follower.user_from.email)
        send_mail(f'{new_post.title}',
                  f'A new article has been posted by {new_post.author.first_name},'
                  f'click on https://www.wetoowrite.com{new_post.get_absolute_url()} to view.',
                  "from.wetoowrite@gmail.com", emails)

        if new_post.is_draft:
            messages.success(self.request, f'Review Your article "{title}" in the Drafts tab!')

        else:
            create_action(self.request.user, "Posted a new article", new_post)
            messages.success(self.request, f'Your article "{title}" has been successfully uploaded for review!')
            send_mail(f'{new_post.title}',
                      f'A new article has been posted by {new_post.author.first_name},'
                      f'click on https://www.wetoowrite.com{new_post.get_absolute_url()} to view.',
                      "from.wetoowrite@gmail.com", ("from.wetoowrite@gmail.com",))

        return super().form_valid(form)


@login_required
def post_draft(request):
    object_list = Post.objects.filter(is_draft=True).filter(author=request.user)
    return render(request, 'blog/post_draft_list.html', {'object_list': object_list, 'title': 'draft'})


@login_required
def post_draft_detail(request, pk):
    post = Post.objects.get(id=pk)
    return render(request, 'blog/post_draft.html', {'object': post, 'title': 'draft'})


@login_required
def post_draft_update(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        print(request.POST, request.FILES.getlist('cover'))
        if form.is_valid():
            posted = form.save(commit=False)
            posted.author = request.user
            posted.is_draft = True if form.cleaned_data['is_draft'] == 'on' else False
            # post.author = request.user
            # title = form.cleaned_data['title']
            # post.title = title
            # post.content = form.cleaned_data['content']
            # post.is_draft = form.cleaned_data['is_draft']
            # if form.cleaned_data['cover']:
            #     post.cover = form.cleaned_data['cover']
            posted.save()
            if posted.is_draft:
                messages.success(request,
                                 f'{post.author.first_name} Click on Review to Edit Your article "{post.title}" !')
                return redirect('post-draft')

            else:
                create_action(request.user, "Posted a new article", post)
                messages.success(request, f'Your article "{post.title}" has been successfully uploaded for review!')
                send_mail(f'{post.title}',
                          f'A new article has been posted by {post.author.first_name},'
                          f'click on https://www.wetoowrite.com{post.get_absolute_url()} to view.',
                          "from.wetoowrite@gmail.com", ("from.wetoowrite@gmail.com",))
            return redirect('blog-home')

    return render(request, 'blog/post_form.html', {'form': form})


class PostUpdate(UpdateView):
    model = Post
    form_class = PostForm
    # success_url = '/post-draft'
    template_name = 'blog/post_form.html'

    # def form_valid(self, form):
    #     post = Post.objects.get(id=self.kwargs['pk'])
    #     is_draft = form.cleaned_data['is_draft']
    #     return super(PostUpdate, self).form_valid(form)

    def get_success_url(self):
        post = Post.objects.get(id=self.kwargs['pk'])
        if post.is_draft:
            messages.success(self.request,
                             f'{post.author.first_name} Click on Review to Edit Your article "{post.title}" !')
            url = reverse('post-draft')
            return url

        else:
            create_action(self.request.user, "Posted a new article", post)
            messages.success(self.request, f'Your article "{post.title}" has been successfully uploaded for review!')
            send_mail(f'{post.title}',
                      f'A new article has been posted by {post.author.first_name},'
                      f'click on https://www.wetoowrite.com{post.get_absolute_url()} to view.',
                      "from.wetoowrite@gmail.com", ("from.wetoowrite@gmail.com",))

            url = reverse('blog-home')
            return url


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


@login_required
def post_delete(request, pk):
    post = Post.objects.get(id=pk)
    return render(request, 'blog/post_confirm_delete.html', {'object': post})


@login_required
def delete_post(request, pk):
    post = Post.objects.get(id=pk)
    post.draft = True
    post.save()
    return redirect('blog-home')


class PostListView(ListView):
    model = Post
    paginate_by = 4

    def get(self, request, *args, **kwargs):
        self.object_list = Post.objects.filter(draft=False)
        article = Post.objects.last()
        try:
            Tracker.objects.create_from_request(request, article)
        except AssertionError:
            pass
        Tracker.objects.filter(Q(device='Other') | Q(device_type='bot') | Q(device='Spider')).delete()
        context = self.get_context_data()
        return self.render_to_response(context)


def detail_view_show(request, pk, year, month, day, post, author):
    post = get_object_or_404(Post, id=pk)
    # post = Post.objects.get(id=pk)
    Tracker.objects.create_from_request(request, post)
    Tracker.objects.filter(Q(device='Other') | Q(device_type='bot') | Q(device='Spider')).delete()
    email_id = post.author.email
    blob = TextBlob(post.content)
    key_words_list = tag_list(post.content)
    sentiment = blob.sentiment
    subjectivity = round(sentiment[0], 2)
    polarity = round(sentiment[1], 3)
    comments = post.comments.filter(active=True)
    tracker_count = ''
    if Tracker.objects.filter(object_id__exact=post.id).exists():
        tracker_count = Tracker.objects.filter(object_id__exact=post.id).count()

    comment_form = CommentsForm(request.POST, request.FILES)
    comment_reply_form = CommentReplyForm(request.POST)
    reply = []
    for comment in comments:
        reply_post = comment.comments_reply.all()
        reply.append(reply_post)
    if request.method == 'POST':
        if comment_form.is_valid():
            name = comment_form.cleaned_data['name']
            email_data = comment_form.cleaned_data['email']
            comm_url = request.build_absolute_uri(post.get_absolute_url())
            print(comm_url)
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            create_action(request.user, 'Posted a new comment on', post)
            send_mail(f'New Comment for your Post {post.title} ',
                      f'A comment has been posted by {name} on {post.title},'
                      f' click on {comm_url}{post.slug}/ to view. Contact the person on email id {email_data}',
                      "from.wetoowrite@gmail.com", [email_id])
            sent = True
            return render(request, 'blog/post_detail.html',
                          {'object': post, 'post': post, 'summary_list': summary(post),
                           'comment_form': CommentsForm(
                               initial={'name': request.user, 'email': request.user.email}),
                           'comments': post.comments.filter(active=True),
                           'comment_reply_form': CommentReplyForm(), 'key_words_list': key_words_list,
                           'comment_replies': reply, 'polarity': polarity, 'subjectivity': subjectivity,
                           'total_views': tracker_count, 'title': post.slug,
                           })

    return render(request, 'blog/post_detail.html', {'object': post, 'post': post, 'summary_list': summary(post),
                                                     'comment_form': CommentsForm(
                                                         initial={'name': request.user,
                                                                  'email': 'from.wetoowrite@gmail.com'}),
                                                     'comments': comments, 'comment_reply_form': CommentReplyForm(),
                                                     'comment_replies': reply, 'polarity': polarity,
                                                     'subjectivity': subjectivity, 'title': post.slug,
                                                     'key_words_list': key_words_list, 'total_views': tracker_count,
                                                     })


def detail_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    # post = Post.objects.get(id=pk)
    Tracker.objects.create_from_request(request, post)
    Tracker.objects.filter(Q(device='Other') | Q(device_type='bot') | Q(device='Spider')).delete()
    email_id = post.author.email
    blob = TextBlob(post.content)
    key_words_list = tag_list(post.content)
    sentiment = blob.sentiment
    subjectivity = round(sentiment[0], 2)
    polarity = round(sentiment[1], 3)
    comments = post.comments.filter(active=True)
    tracker_count = ''
    if Tracker.objects.filter(object_id__exact=post.id).exists():
        tracker_count = Tracker.objects.filter(object_id__exact=post.id).count()

    comment_form = CommentsForm(request.POST, request.FILES)
    comment_reply_form = CommentReplyForm(request.POST)
    reply = []
    for comment in comments:
        reply_post = comment.comments_reply.all()
        reply.append(reply_post)
    if request.method == 'POST':
        if comment_form.is_valid():
            name = comment_form.cleaned_data['name']
            email_data = comment_form.cleaned_data['email']
            comm_url = request.build_absolute_uri(post.get_absolute_url())
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            create_action(request.user, 'Posted a new comment on', post)
            send_mail(f'New Comment for your Post {post.title} ',
                      f'A comment has been posted by {name} on {post.title},'
                      f' click on {comm_url}{post.slug}/ to view. Contact the person on email id {email_data}',
                      "from.wetoowrite@gmail.com", [email_id])
            sent = True
            return render(request, 'blog/post_detail.html',
                          {'object': post, 'post': post, 'summary_list': summary(post),
                           'comment_form': CommentsForm(
                               initial={'name': request.user, 'email': request.user.email}),
                           'comments': post.comments.filter(active=True),
                           'comment_reply_form': CommentReplyForm(), 'key_words_list': key_words_list,
                           'comment_replies': reply, 'polarity': polarity, 'subjectivity': subjectivity,
                           'total_views': tracker_count, 'title': post.slug,
                           })

    return render(request, 'blog/post_detail.html', {'object': post, 'post': post,
                                                     'summary_list': summary(post) if summary(
                                                         post) is not False else False,
                                                     'comment_form': CommentsForm(
                                                         initial={'name': request.user,
                                                                  'email': 'from.wetoowrite@gmail.com'}),
                                                     'comments': comments, 'comment_reply_form': CommentReplyForm(),
                                                     'comment_replies': reply, 'polarity': polarity,
                                                     'subjectivity': subjectivity, 'title': post.slug,
                                                     'key_words_list': key_words_list, 'total_views': tracker_count,
                                                     })


@login_required
def comment_update(request, pk, idx):
    form = CommentsForm(request.POST)
    post = Post.objects.get(id=idx)
    if form.is_valid():
        body = form.cleaned_data['body']
        comment = Comments.objects.get(id=pk)
        comment.body = body
        comment.save()
    else:
        print('not valid')
    # redirect to a model obj instance
    return redirect(post)


@login_required
def reply_delete(request, pk, idx):
    post = Post.objects.get(id=idx)
    reply = CommentReply.objects.get(id=pk)
    reply.delete()
    return redirect(post)


@login_required
def comment_delete(request, pk, idx):
    post = Post.objects.get(id=idx)
    comment = Comments.objects.get(id=pk)
    comment.delete()
    return redirect(post)


class PostUpdateView(UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name_suffix = '_update_form'

    # to override author
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        # to authenticate user and author are same

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def reply_ajax(request):
    comment_reply_form = CommentReplyForm(request.POST)
    if request.method == 'POST':
        if comment_reply_form.is_valid():
            id = request.POST.get('com_id')
            name = comment_reply_form.cleaned_data['name']
            reply = comment_reply_form.cleaned_data['reply']
            new_comment_reply = comment_reply_form.save(commit=False)
            new_comment_reply.comments = Comments.objects.get(id=id)
            new_comment_reply.user = request.user
            new_comment_reply.save()
            comment = Comments.objects.get(id=id)
            create_action(get_current_user(), 'replied to a comment on', comment.post)
            response = {'name': name, 'reply': reply}
            return JsonResponse(response)


@login_required
@require_POST
def post_like(request):
    # 'id','action' being passed as 'data-id/action in a tag
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        post = Post.objects.get(id=post_id)
        if action == 'like':
            post.users_like.add(request.user)
            create_action(request.user, "Liked Post", post)
        else:
            post.users_like.remove(request.user)
            create_action(request.user, "Unliked Post", post)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'not_ok'})


@login_required
@require_POST
def follow_users(request):
    # 'id','action' being passed as 'data-id/action in a tag
    follower_id = request.POST.get('id')
    action = request.POST.get('action')

    if follower_id and action:
        user = User.objects.get(id=follower_id)
        if action == 'follow':
            Contact.objects.get_or_create(
                user_from=request.user,
                user_to=user
            )
            create_action(request.user, "Followed", user)
        else:
            Contact.objects.filter(
                user_from=request.user,
                user_to=user
            ).delete()
            create_action(request.user, "Unfollowed", user)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'not_ok'})


def twitter_post(screen_names, count):
    API_key = 'H6ybab13ZU5cdaUnj6KtP5AMI'
    API_secret = 'VXwYC9cmCnOqVzEpvWonVMqbUBtDX8KiUm40lpIzrz2IadNeeN'
    access_token = '1667776874-rBHAOHpytghmzJUEB7rs6gRi2cqWt3oja9jDF0k'
    access_token_secret = 'TyAztICP2ZU6nEUxgLuGDDmQLVV495YSDW97sRpCnPaYX'
    auth = tw.OAuthHandler(API_key, API_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    all_tweets = []
    for name in screen_names:
        new_tweets = api.user_timeline(screen_name=name, count=count)
        all_tweets.extend(new_tweets)
    if not hasattr(all_tweets, 'retweeted_status'):
        return all_tweets


def check_text(tweets):
    tweet_clone = tweets.copy()
    tweets.clear()
    for tweet in tweet_clone:
        length = len(tweet.entities['user_mentions'])
        if length == 0 and not tweet.text.startswith('@'):
            tweets.append(tweet)
    return tweets


def twitter_posts(request):
    list_url = []
    list_name = []
    list_vol = []
    zip_data = zip()
    trends1 = []
    form = TrendsForm()
    screen_names = ['EconomicTimes', 'nytimes', 'htTweets', 'timesofindia', 'TOIIndiaNews', 'ETpanache', 'ETNOWlive',
                    'dna', 'soundarya_20', 'SrBachchan', 'AnupamPKher', 'radhika_apte', 'DishPatani', 'taapsee',
                    'narendramodi', 'ANI', 'firstpost', 'finshots']
    API_key = 'H6ybab13ZU5cdaUnj6KtP5AMI'
    API_secret = 'VXwYC9cmCnOqVzEpvWonVMqbUBtDX8KiUm40lpIzrz2IadNeeN'
    access_token = '1667776874-rBHAOHpytghmzJUEB7rs6gRi2cqWt3oja9jDF0k'
    access_token_secret = 'TyAztICP2ZU6nEUxgLuGDDmQLVV495YSDW97sRpCnPaYX'
    auth = tw.OAuthHandler(API_key, API_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    selected = get_trends()
    add_list = []
    for i in range(len(selected)):
        add_list.append(selected[i][1])
    if request.method == 'POST':
        form = TrendsForm(request.POST)
        if form.is_valid():
            input_data = form.cleaned_data
            country_index = ([x for x, y in enumerate(selected) if y[1] == input_data])
            try:
                woe_id = selected[country_index[0]][0]
            except Exception:
                messages.warning(request, f'Enter a proper Country! Showing Trends for India')
                woe_id = ''
            trends1 = api.trends_place(woe_id) if woe_id else api.trends_place(23424848)
            for trend in range(8):
                data = trends1[0]['trends'][trend]
                list_name.append(data['name'])
                list_url.append(data['url'])
                list_vol.append(data['tweet_volume'])
            zip_data = zip(list_name, list_url, list_vol)

            context = {
                'function': twitter_post(screen_names, 50),
                'name': zip_data,
                'form': form,
                'new_list': add_list,
                'selected': input_data,

            }
            return render(request, 'blog/twitter.html', context)
        else:
            form = TrendsForm()
    zip_data = zip(list_name, list_url, list_vol)

    context = {
        'function': check_text(twitter_post(screen_names, 50)),
        'name': zip_data,
        'form': form,
        'new_list': add_list,
    }
    return render(request, 'blog/twitter.html', context)


def search_twitter(request):
    API_key = 'H6ybab13ZU5cdaUnj6KtP5AMI'
    API_secret = 'VXwYC9cmCnOqVzEpvWonVMqbUBtDX8KiUm40lpIzrz2IadNeeN'
    access_token = '1667776874-rBHAOHpytghmzJUEB7rs6gRi2cqWt3oja9jDF0k'
    access_token_secret = 'TyAztICP2ZU6nEUxgLuGDDmQLVV495YSDW97sRpCnPaYX'
    auth = tw.OAuthHandler(API_key, API_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    if request.method == 'POST':
        search_form = TwitterSearchForm(request.POST)
        if search_form.is_valid():
            search_word = search_form.cleaned_data
            search_results = api.search(q=search_word, count=100)
            search_tweeter = []
            c_polarity_sum = 0
            c_polarity_count = 0
            avg_c_polarity = 0
            for item in search_results:
                user = item._json['user']
                text = item._json['text']
                name = user['screen_name']
                location = user['location']
                image = user['profile_image_url_https']
                info = item._json['entities']
                s = TextBlob(item.text)
                polarity = round(s.sentiment[0], 2)
                objectivity = round(s.sentiment[1], 2)
                um = info['urls']
                url = ''
                if len(um) == 0:
                    url = 'none'
                elif len(um) > 0:
                    url = um[0]['expanded_url']
                re_tweets = None
                likes = None
                c_polarity = ''
                c_objectivity = ''
                if 'retweeted_status' in item._json.keys():
                    re_tweets = item.retweeted_status.retweet_count
                    likes = item.retweeted_status.favorite_count
                    c_polarity = polarity * re_tweets
                    c_objectivity = objectivity * re_tweets
                if re_tweets and polarity:
                    c_polarity = re_tweets * polarity
                    c_polarity_sum += c_polarity
                    c_polarity_count += 1

                items = (image, name, text, location, url, objectivity, polarity, re_tweets, likes, c_polarity)
                search_tweeter.append(items)

            if c_polarity_count and c_polarity_sum:
                try:
                    avg_c_polarity = c_polarity_sum / c_polarity_count
                    print(avg_c_polarity)
                except:
                    pass

            context = {
                'search_form': search_form,
                'search_results': list(set(search_tweeter)),
                'avg_c_polarity': round(avg_c_polarity, 3),
            }
            return render(request, 'blog/search_twitter.html', context)

    else:
        search_form = TwitterSearchForm()
    context = {
        'search_form': search_form,
    }
    return render(request, 'blog/search_twitter.html', context)


def handler404(request, exception=None):
    return render(request, 'blog/404.html', status=404)


def handler500(request, exception=None):
    return render(request, 'blog/500.html', status=500)


class LenSpeakListView(ListView):
    model = PhotoStory


@login_required
def create_photo_story(request):
    context = {
        # 'photos': Photo.objects.filter(photo_story__user=request.user),
        'form': PhotoForm(),
        'story_form': PhotoStoryForm(),
    }
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        photo_story = PhotoStory()
        story_form = PhotoStoryForm(request.POST)
        if form.is_valid() and story_form.is_valid():
            # save story
            photo_story.story_title = story_form.cleaned_data.get('story_title', None)
            photo_story.story_content = story_form.cleaned_data.get('story_content', None)
            photo_story.user = request.user
            photo_story.save(PhotoStory)
            # save pics
            photo = Photo()
            photo.file = form.cleaned_data['file']
            photo.title_of_the_picture = form.cleaned_data['title_of_the_picture']
            photo.describe_the_picture = form.cleaned_data['describe_the_picture']
            photo.photo_story = PhotoStory.objects.latest('uploaded_at')
            print(photo.title_of_the_picture, 'photo')
            photo.save(Photo)
            create_action(request.user, 'Posted a new Photo Story on', photo_story)
            Tracker.objects.create_from_request(request, photo_story)
            Tracker.objects.filter(Q(device='Other') | Q(device_type='bot') | Q(device='Spider')).delete()
            context = {
                'story': PhotoStory.objects.latest('uploaded_at'),
                'photos': Photo.objects.filter(photo_story=PhotoStory.objects.latest('uploaded_at').id)

            }
            return render(request, 'blog/photo_gallery.html', context)

    return render(request, 'blog/upload_images.html', context)


@login_required
def make_photo_story(request):
    context = {
        'form': PhotoForm(),
        'story_form': PhotoStoryForm(),
    }
    if request.method == "POST":
        form = PhotoStoryForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')
        if form.is_valid() and photo_form.is_valid():
            new_story = form.save(commit=False)
            new_story.user = request.user
            new_story.save()
            photo_story = PhotoStory.objects.latest('uploaded_at')
            story_title = form.cleaned_data['story_title']
            for file in files:
                new_photo = photo_form.save(commit=False)
                new_photo.photo_story = photo_story
                new_photo.file = file
                new_photo.save()
            create_action(request.user, 'Posted a new Photo Story on', photo_story)
            Tracker.objects.create_from_request(request, photo_story)
            Tracker.objects.filter(Q(device='Other') | Q(device_type='bot') | Q(device='Spider')).delete()
            new_picture_story = PhotoStory.objects.filter(story_title=story_title)
            new_picture_story = new_picture_story.first() if new_picture_story.count()>0 else None
            context = {
                'story': photo_story,
                'photos': Photo.objects.filter(photo_story=photo_story.id)

            }
            return redirect(new_picture_story)

    return render(request, 'blog/upload_images.html', context)


@login_required
def add_photo_to_story(request, pk):
    story = get_object_or_404(PhotoStory, id=pk)
    context = {
        'photos': Photo.objects.filter(photo_story_id=story.id),
        'story': story,
        'form': PhotoForm(),

    }
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        photo = Photo()
        if form.is_valid():
            for field in request.FILES.keys():
                for form_file in request.FILES.getlist(field):
                    new_photo = Photo()
                    new_photo.file = form_file
                    new_photo.title_of_the_picture = form.cleaned_data['title_of_the_picture']
                    new_photo.describe_the_picture = form.cleaned_data['describe_the_picture']
                    new_photo.photo_story = story
                    new_photo.save(Photo)
            return redirect(story)
    return render(request, 'blog/upload_images.html', context)


def large_file(request, pk):
    story = get_object_or_404(PhotoStory, id=pk)
    context = {
        'photos': Photo.objects.filter(photo_story_id=story.id),
        'story': story,
        'form': PhotoForm(),
        'story_id': pk,

    }
    if request.method == 'POST':
        new_photo = Photo()
        new_photo.file = request.POST['file']
        new_photo.title_of_the_picture = request.POST['title_of_the_picture']
        new_photo.describe_the_picture = request.POST['describe_the_picture']
        new_photo.photo_story = story
        new_photo.save(Photo)
        return redirect(story)

    return render(request, 'blog/large_upload.html', context)


def large_file_direct(request):
    S3_BUCKET = 'wetoowrite'
    file_name = request.GET['file_name']
    file_type = request.GET['file_type']
    # my_config = Config(
    # region_name='ap-south-1',
    # signature_version='s3v4',
    # )

    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_S3_REGION_NAME
                      )

    presigned_post = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=f'{request.user}/{file_name}',
        Fields={"acl": "public-read",
                "Content-Type": file_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": file_type},
        ],
        ExpiresIn=3600,
    )
    print(presigned_post)
    response = {
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    }

    return JsonResponse(response, safe=False)


def update_db(request):
    data = request.POST
    print(data)
    pk = data.get('story_id')
    story = get_object_or_404(PhotoStory, id=int(pk))
    Photo.objects.create(photo_story=story, title_of_the_picture=data.get('title'),
                         describe_the_picture=data.get('description'),
                         file=data.get('uploadedFile'))

    return JsonResponse({'response': 'success'})


class PhotoUpdateView(UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = Photo
    form_class = PhotoForm
    template_name_suffix = '_update_form'
    context_object_name = 'object'

    # to override author
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        # to authenticate user and author are same

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class StoryUpdateView(UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = PhotoStory
    form_class = PhotoStoryForm
    template_name_suffix = '_update_form'
    context_object_name = 'object'

    # to override author
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        # to authenticate user and author are same

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def photo_story_view(request, pk, tale, author, year, month, day):
    story = PhotoStory.objects.get(id=pk)

    photos = Photo.objects.filter(photo_story_id=story.id)
    Tracker.objects.create_from_request(request, story)
    Tracker.objects.filter(Q(device='Other') | Q(device_type='bot') | Q(device='Spider')).delete()
    pic_list = []
    video_list = []
    if photos.count() > 0:
        for photo in photos:
            file_name = photo.file
            if str(file_name).endswith('mp4') or str(file_name).endswith('webm'):
                video_list.append(photo)
            else:
                pic_list.append(photo)
    context = {
        'photos': pic_list if len(pic_list) > 0 else None,
        'videos': video_list if len(video_list) > 0 else None,
        'story': story,
    }
    return render(request, 'blog/photo_gallery.html', context)


@login_required
def clear_database(request, pk, story_pk):
    Photo.objects.get(id=pk).delete()
    return redirect('upload-images', story_pk)


@login_required
def delete_story(request, pk):
    story = PhotoStory.objects.get(id=pk)
    Tracker.objects.create_from_request(request, story)
    try:
        tgt = ContentType.objects.get_for_model(PhotoStory)
        action = Action.objects.get(target_id=story.id, target_ct=tgt.id)
        action.delete()
    except:
        pass
    story.delete()
    messages.success(request, f'{story.story_title} deleted')
    return redirect('picture-story-list')
