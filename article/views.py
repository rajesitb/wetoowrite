from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.template import loader
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from blog.models import Contact, Action

from .models import Article, Comments, CommentReply
from .forms import ArticleForm, CommentReplyForm, CommentsForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from tracking_analyzer.models import Tracker
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Create your views here.

from blog.utils import create_action


class ArticleCreate(CreateView):
    model = Article
    form_class = ArticleForm
    success_url = '/article-show/'
    template_name = 'article/form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        new_article = form.save(commit=False)
        new_article.save()
        create_action(self.request.user, "Posted a new article", new_article)
        return super().form_valid(form)


def article_show(request):
    article = Article.objects.first()
    return article_show_all(request, article.id, article.slug, article.author,
                            article.publish.year, article.publish.month,
                            article.publish.day)


def article_show_all(request, pk, slug, author, year, month, day):
    post = get_object_or_404(Article, id=pk)
    articles = Article.objects.all()
    Tracker.objects.create_from_request(request, post)
    Tracker.objects.filter(Q(device='Other') | Q(device_type='bot') | Q(device='Spider')).delete()
    comments = post.comments_article.filter(active=True)
    tracker_count = ''
    if Tracker.objects.filter(object_id__exact=post.id).exists():
        tracker_count = Tracker.objects.filter(object_id__exact=post.id).count()
    reply = []
    for comment in comments:
        reply_post = comment.comments_reply_article.all()
        reply.append(reply_post)
    if request.user.is_authenticated:
        comment_form = CommentsForm(initial={'name': request.user, 'email': request.user.email})
    else:
        comment_form = CommentsForm()

    context = {
        'comment_reply_form': CommentReplyForm(),
        'article': post,
        'comments': comments,
        'comment_replies': reply,
        'total_views': tracker_count,
        'articles': articles,
        'title': post.slug,
    }
    return render(request, 'article/article.html', context)


def comment_update(request, pk, idx):
    form = CommentsForm(request.POST)
    comment = Comments.objects.get(id=pk)
    if form.is_valid():
        body = form.cleaned_data['body']
        comment.body = body
        comment.save()
        return redirect(comment)
    else:
        print('not valid')
    return redirect(comment)


def reply_delete(request, pk, idx):
    reply = get_object_or_404(CommentReply, id=pk)
    reply.delete()
    # learn how variables are passed in redirect
    return redirect(reply.comments)


def comment_delete(request, pk, idx):
    comment = get_object_or_404(Comments, id=pk)
    comment.delete()
    # learn how variables are passed in redirect
    return redirect(comment)


class ArticleUpdateView(UpdateView, UserPassesTestMixin):
    model = Article
    form_class = ArticleForm
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


class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy('article-show')


def create_comment(request, pk, slug):
    if request.user.is_authenticated:
        comment_form = CommentsForm(initial={'name': request.user, 'email': request.user.email})
    else:
        comment_form = CommentsForm()
    post = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        comment_form = CommentsForm(request.POST, request.FILES)
        if comment_form.is_valid():
            print(comment_form)
            email_id = post.author.email
            name = comment_form.cleaned_data['name']
            email_data = comment_form.cleaned_data['email']
            comment = comment_form.cleaned_data['body']
            comm_url = post.get_absolute_url()
            new_comment = comment_form.save(commit=False)
            new_comment.article = post
            new_comment.save()
            print(new_comment)
            create_action(request.user, 'Posted a new comment on', post)
            send_mail(f'New Comment for your Article {post.title} ',
                      f'A comment has been posted by {name} on {post.title},'
                      f' click on https://www.wetoowrite.com{comm_url} to view. Contact the person on email id {email_data}',
                      "from.wetoowrite@gmail.com", [email_id])
            return redirect(post)
    return render(request, 'article/comments_form.html', {'form': comment_form, 'article': post, 'title': post.slug})


class CommentUpdateView(UpdateView, UserPassesTestMixin):
    model = Comments
    form_class = CommentsForm
    template_name_suffix = '_update_form'
    # success_url = '/article-show-all/<int:pk>/<slug:slug>/'

    # to override author
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            return super().form_valid(form)
        return super().form_invalid(form)
        # to authenticate user and author are same

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.name:
            return True
        return False


def reply_ajax(request):
    comment_reply_form = CommentReplyForm(request.POST)
    if request.method == 'POST':
        if comment_reply_form.is_valid():
            id = request.POST.get('com_id')
            reply = comment_reply_form.cleaned_data['reply']
            new_comment_reply = comment_reply_form.save(commit=False)
            new_comment_reply.comments = Comments.objects.get(id=id)
            new_comment_reply.name = request.user.first_name
            new_comment_reply.save()
            comment = Comments.objects.get(id=id)
            create_action(request.user, 'replied to a comment on', comment.article)
            response = {'name': new_comment_reply.name, 'reply': reply}
            return JsonResponse(response)


@login_required
@require_POST
def article_like(request):
    # 'id','action' being passed as 'data-id/action in a tag
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        post = Article.objects.get(id=post_id)
        if action == 'like':
            post.users_like.add(request.user)
            create_action(request.user, "Liked Article", post)
        else:
            post.users_like.remove(request.user)
            create_action(request.user, "Unliked Article", post)
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


