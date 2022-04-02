import logging

from django.shortcuts import render

import urllib.request
import requests
from .forms import GetNews
from django.http import JsonResponse


countries = (
    ('Argentina', 'ar'), ('Austria', 'at'), ('Australia', 'au'), ('Belgium', "be"), ('Bulgaria', 'bg'),
    ('Brazil', 'br'),
    ('Canada', 'ca'), ('China', 'cn'), ('Combodia', 'co'), ('Cuba', 'cu'), ('Czech', 'cz'), ('Germany', 'de'),
    ('Egypt', 'eg'), ('France', 'fr'), ('Britain', 'gb'), ('Greece', 'gr'), ('HongKong', 'hk'), ('Hungary', 'hu'),
    ('Indonesia', 'id'), ('Ireland', 'ie'), ('Israel', 'il'), ('India', 'in'), ('Italy', 'it'), ('Japan', 'jp'),
    ('Korea', 'kr'), ('New Zealand', 'nz'), ('Russia', 'ru'), ('Sweden', 'se'), ('Singapore', 'sg'), ('Thailand', 'th'),
    ('Turkey', 'tr'), ('Taiwan', 'tw'), ('USA', 'us'), ('South Africa', 'za'))

cat = (('business', 'business'), ('entertainment', 'entertainment'), ('general', 'general'), ('health', 'health'),
       ('science', 'science'), ('sports', 'sports'), ('technology', 'technology'))


def news_search(request):
    api_key = '03e6fb17fbfa4e809aca75b261067606'
    search_cat = ''
    search_country = ''
    news = ''
    if request.method == 'POST':
        form = GetNews(request.POST)
        if form.is_valid():
            search_news = form.cleaned_data['search_term']
            if form.cleaned_data['country']:
                country = form.cleaned_data['country']
                search_country = dict(countries)[country]
            if form.cleaned_data['category']:
                category = form.cleaned_data['category']
                search_cat = dict(cat)[category]
            url = ('https://newsapi.org/v2/top-headlines?q={}&country={}&category={}&language=en&apiKey={}'.format(
                search_news,
                search_country,
                search_cat,
                api_key))
            response = requests.get(url)
            news = response.json()
            context = {
                'form': form,
                'articles': news,
                'countries': list(countries),
                'cat': list(cat),
            }
            return render(request, 'news/search-news.html', context)
    else:
        form = GetNews()
        search_country = 'India'
        search_news = 'general'
        url = ('https://newsapi.org/v2/top-headlines?q={}&country={}&category={}&language=en&apiKey={}'.format(
            search_news,
            search_country,
            search_cat,
            api_key))
        response = requests.get(url)
        news = response.json()

    context = {
        'form': form,
        'articles': news,
        'countries': list(countries),
        'cat': list(cat),
    }
    return render(request, 'news/search-news.html', context)


def auto_search_news(request):
    api_key = '03e6fb17fbfa4e809aca75b261067606'
    form = GetNews(request.GET)
    if form.is_valid():

        search_data = form.cleaned_data.get('search_term')
        url = ('https://newsapi.org/v2/top-headlines?q={}&language=en&pageSize=10&apiKey={}'.format(search_data, api_key))
        response = requests.get(url)
        news = response.json()
        print('response', news.get('status'))
        logging.info(f'{news}')
        # to serialize non-dict object
        if news.get('status') == 'ok':
            return JsonResponse(news['articles'], safe=False)
        else:
            return JsonResponse({'error': 'no response'})
    return JsonResponse({'error': 'no response'})



