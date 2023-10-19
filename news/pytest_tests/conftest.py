from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

NEWS_TITLE = 'Заголовок новости'
NEWS_TEXT = 'Текст новости'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title=NEWS_TITLE,
        text=NEWS_TEXT,
    )


@pytest.fixture
def news_pk_for_args(news):
    return news.pk,


@pytest.fixture
def news_set(db):
    return News.objects.bulk_create(
        News(
            title=f'{NEWS_TITLE} {index}',
            text=NEWS_TEXT,
            date=timezone.now().date() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news,
    )


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def url_to_comment(comment):
    return reverse('news:detail', args=(comment.news.pk,)) + '#comments'


@pytest.fixture
def comment_set(author, news):
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def form_data():
    return {'text': 'Новый текст комментария'}
