from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        client, form_data, news_detail_url,
):
    client.post(news_detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        reader, news, news_detail_url, form_data, reader_client,
):
    response = reader_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == reader


def test_user_cant_use_bad_words(reader_client, news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'}
    response = reader_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response, 'form', 'text', errors=WARNING,
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client, comment_delete_url, url_to_comment,
):
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comment)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        reader_client, comment_delete_url,
):
    response = reader_client.delete(comment_delete_url)
    assert response.status_code, HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        comment, author_client, comment_edit_url, url_to_comment, form_data,
):
    response = author_client.post(comment_edit_url, data=form_data)
    assertRedirects(response, url_to_comment)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        reader_client, comment_edit_url, comment, form_data,
):
    comment_text_before_edit = comment.text
    response = reader_client.post(comment_edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text_before_edit
