from django import template
from django.db.models import Count, Q
from ..models import Post, Action, Photo
# from ..views import post_ranking
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)
import operator
from tracking_analyzer.models import Tracker
from better_profanity import profanity

from article.models import Article

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.objects.count()


@register.inclusion_tag('blog/latest.html')
def show_latest_posts(count=5):
    latest_posts = Post.objects.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def most_commented_post():
    posts = Post.objects.all()
    articles = Article.objects.all()
    most_commented = {}
    for post in posts:
        comments = post.comments.filter(active=True)
        most_commented[post] = comments.count()
    for article in articles:
        comments = article.comments_article.all()
        most_commented[article] = comments.count()
    new_dict = dict([(value, key) for key, value in most_commented.items()])
    new_list = sorted(new_dict, reverse=True)
    sorted_posts = []
    for i in new_list:
        sorted_posts.append(new_dict[i])
    return sorted_posts[:5]


@register.simple_tag
def user_action(user):
    if user.is_authenticated:
        user_actions = Action.objects.exclude(user=user)
    else:
        user_actions = Action.objects.all()
    return user_actions[:5]


@register.simple_tag
def total_likes():
    post = Post.objects.all()
    articles = Article.objects.all()
    liked_count = {}
    for post_like in post:
        liked_count[post_like.title] = post_like.users_like.count()
    for post_like in articles:
        liked_count[post_like.title] = post_like.users_like.count()
    sorted_liked_count = dict(sorted(liked_count.items(), key=operator.itemgetter(1), reverse=True))
    slice_liked_count = dict(list(sorted_liked_count.items())[0: 5])
    return slice_liked_count


@register.simple_tag
def most_viewed():
    posts = Post.objects.all()
    articles = Article.objects.all()
    post_id_list = []
    for post in posts:
        post_id_list.append(post.id)
    for article in articles:
        post_id_list.append(article.id)
    tracker_count = {}
    for item in post_id_list:
        if Tracker.objects.filter(object_id__exact=item).exists():
            try:
                tracker_count[Post.objects.get(id=item)] = Tracker.objects.exclude(object_id=1).filter(object_id__exact=item).count()
            except:
                tracker_count[Article.objects.get(id=item)] = Tracker.objects.filter(object_id__exact=item).count()

    tracker_count_reversed = {k: v for k, v in sorted(tracker_count.items(), key=lambda item: item[1], reverse=True)}
    tracker_count_reversed_out = dict(list(tracker_count_reversed.items())[: 5])
    return tracker_count_reversed_out


@register.filter
def profanity_check(obj):
    return profanity.censor(obj)


@register.simple_tag
def media_pics(story_id):
    pics = Photo.objects.filter(photo_story_id=story_id).\
        filter(Q(file__endswith='.jpg') | Q(file__endswith='.png') | Q(file__endswith='.webp'))
    return pics


@register.simple_tag
def media_video(story_id):
    videos = Photo.objects.filter(photo_story_id=story_id).filter(Q(file__endswith='.mp4') | Q(file__endswith='.webm'))
    return videos


@register.filter
def split_string(value, key):
    user = list(value.split(key))
    return user[len(user)-1].capitalize()


@register.simple_tag
def file_ends_with(value):
    result = any([value.name.endswith('.mp4'), value.name.endswith('.webm')])
    return result

