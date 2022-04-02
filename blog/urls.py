from django.urls import path
from . import views
from django.urls import path, register_converter
from datetime import datetime


class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value


register_converter(DateConverter, 'yyyy')


urlpatterns = [
    path('post-create/', views.PostCreate.as_view(), name='blog-post'),
    path('picture-story/', views.make_photo_story, name='picture-story'),
    path('add-picture-story/<int:pk>/', views.add_photo_to_story, name='add-picture-story'),
    path('delete-picture-story/<int:pk>/', views.delete_story, name='delete-picture-story'),

    path('picture-story-list/', views.LenSpeakListView.as_view(), name='picture-story-list'),
    path('picture-story-view/<int:pk>/<int:year>-<int:month>-<int:day>/<str:author>/<slug:tale>/',
         views.photo_story_view,
         name='picture-story-view'),
    path('picture-update/<int:pk>/', views.PhotoUpdateView.as_view(), name='picture-update'),
    path('picture-story-update/<int:pk>/<slug:tale>/<str:author>/', views.StoryUpdateView.as_view(),
         name='picture-story-update'),

    path('upload-images/<int:pk>/', views.add_photo_to_story, name='upload-images'),
    path('images-large/<int:pk>/', views.large_file, name='images-large'),
    path('images-large-direct/', views.large_file_direct, name='images-large-direct'),
    path('update-db/', views.update_db, name='update-db'),

    path('clear-images/<int:pk>/<int:story_pk>/', views.clear_database, name='clear-database'),

    path('post-draft/', views.post_draft, name='post-draft'),
    path('post-draft-detail/<int:pk>/', views.post_draft_detail, name='post-draft-detail'),
    path('post-draft-update/<int:pk>/', views.PostUpdate.as_view(), name='post-draft-update'),

    path('post-detail/<int:pk>/<int:year>-<int:month>-<int:day>/<slug:post>/<str:author>/',
         views.detail_view_show, name='post-detail-show'),
    path('post-detail/<int:pk>/', views.detail_view, name='post-detail'),

    path('post/<int:pk>/update', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/', views.post_delete, name='post-delete'),
    path('post-delete/<int:pk>/', views.delete_post, name='delete-post'),
    path('comment/<int:pk>/<int:idx>/', views.comment_update, name='comment-update'),
    path('reply/<int:pk>/<int:idx>', views.reply_delete, name='reply-delete'),
    path('comment/<int:pk>/<int:idx>', views.comment_delete, name='comment-delete'),
    path('comment_reply/', views.reply_ajax, name='blog-comment-reply'),
    path('post-like/', views.post_like, name='post-like'),
    path('follow/', views.follow_users, name='follow'),
    path('twitter/', views.twitter_posts, name='blog-twitter'),
    path('twitter-search/', views.search_twitter, name='blog-twitter-search'),
    path('search/', views.search_view, name='blog-search'),
    path('about/', views.about, name='blog-about'),
    path('tnc/', views.tnc, name='blog-tnc'),
    path('privacy/', views.privacy, name='privacy'),
    path('author/<int:pk>/<str:author>', views.UserPostListView.as_view(), name='user-posts'),

    path('', views.PostListView.as_view(), name='blog-home'),

]