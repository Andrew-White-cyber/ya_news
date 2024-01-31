from django.urls import reverse
from django.test.client import Client
from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus

from news.models import Comment


def test_anonymous_user_cant_create_comment(form_data, news):
    """Аноним не может создать коммент."""
    client = Client()
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client, author, news, form_data):
    """Авторизованный пользователь может создавать комменты."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(bad_words, news, not_author_client):
    """Никаких ругательств."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {bad_words[0]}, еще текст'}
    warning = 'Не ругайтесь!'
    response = not_author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=warning
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment, news):
    """Автор может удалять свои комменты."""
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(comment, not_author_client):
    """Нельзя удалить комменты других пользователей."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        comment,
        news,
        updated_form_data,
        author_client
        ):
    """Автор может редактировать свои комменты."""
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=updated_form_data)
    comment.refresh_from_db()
    assertRedirects(response, url_to_comments)
    assert comment.text == updated_form_data['text']


def test_user_cant_edit_comment_of_another_user(
        comment,
        not_author_client,
        updated_form_data
        ):
    """Нельзя редактировать чужие комменты."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=updated_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
