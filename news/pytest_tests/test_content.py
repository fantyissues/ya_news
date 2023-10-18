import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm
from news.models import News

HOME_URL = reverse('news:home')


@pytest.mark.usefixtures('news_set')
def test_news_count(client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('news_set')
def test_news_order(client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('comment_set')
def test_comments_order(client, news):
    response = client.get(reverse('news:detail', args=(news.pk,)))
    assert 'news' in response.context
    news = response.context['news']
    assert isinstance(news, News)
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_anonymous_client_has_no_form(client, news):
    response = client.get(reverse('news:detail', args=(news.pk,)))
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    response = author_client.get(reverse('news:detail', args=(news.pk,)))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
