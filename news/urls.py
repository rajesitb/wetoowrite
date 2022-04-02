from django.urls import path

from .views import (
                    news_search,
                    auto_search_news,

                    )

urlpatterns = [

    path('search-news/', news_search, name='search-news'),
    path('search-live/', auto_search_news, name='auto-search-news'),

]