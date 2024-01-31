from datetime import datetime, timedelta
from django.conf import settings
from django.test.client import Client
from news.models import News, Comment
from django.urls import reverse
import pytest


def test_news_count(all_news, not_author_client):
    News.objects.bulk_create(all_news)
    response = not_author_client.get(reverse('news:home'))
    object_list = response.context['object_list']
    # Определяем длину списка.
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(all_news, not_author_client):
    News.objects.bulk_create(all_news)
    response = not_author_client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates

@pytest.mark.usefixtures('add_two_comments')
def test_comments_order(news, not_author_client):
    detail_url = reverse('news:detail', args=(news.id,))
    response = not_author_client.get(detail_url)
    assert 'news' in response.context
    news_obj = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news_obj.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_anonymous_client_has_no_form(news):
    client = Client()
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = not_author_client.get(detail_url)
    assert 'form' in response.context
