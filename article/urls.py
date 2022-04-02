from django.urls import path
from . import views
urlpatterns = [
    path('article-show/', views.article_show, name='article-show'),
    path('article-show-all/<int:pk>/<slug:slug>/<str:author>/<int:year>-<int:month>-<int:day>/',
         views.article_show_all, name='article-show-all'),
    path('article-comment/<int:pk>/<slug:slug>/', views.create_comment, name='article-comment-create'),
    path('article-update/<int:pk>/<slug:slug>/', views.ArticleUpdateView.as_view(), name='article-update'),
    path('article-delete/<int:pk>/', views.ArticleDeleteView.as_view(), name='article-delete'),
    path('comment-update/<int:pk>/', views.CommentUpdateView.as_view(), name='comment-update'),

    path('article_comment_reply/', views.reply_ajax, name='article-comment-reply'),
    path('article-like/', views.article_like, name='article-like'),
    path('article-follow/', views.follow_users, name='article-follow'),
    # path('article-comment-update/<int:pk>/<int:idx>/', views.comment_update, name='article-comment-update'),
    path('article-delete-comment/<int:pk>/<int:idx>', views.comment_delete, name='article-comment-delete'),
    path('article-reply/<int:pk>/<int:idx>', views.reply_delete, name='article-reply-delete'),

    path('form-article/', views.ArticleCreate.as_view(), name='article-form'),
    ]

