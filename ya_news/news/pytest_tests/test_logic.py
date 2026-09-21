from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING

FORM_DATA = {
    'text': 'Новый текст',
}


def test_creating_comment_is_unavailable_to_anonymous_user(
    news_url_detail,
    client,
    test_news,
):
    comments_before = test_news.comment_set.count()
    response = client.post(news_url_detail, data=FORM_DATA)
    comments_after = test_news.comment_set.count()

    assert response.status_code == HTTPStatus.FOUND
    assert comments_after == comments_before


def test_success_creating_comment_by_authenticated_user(
    news_url_detail,
    reader_client,
    reader,
    test_news,
):
    response = reader_client.post(news_url_detail, data=FORM_DATA)

    assertRedirects(response, news_url_detail + '#comments')
    assert test_news.comment_set.count() == 1
    comment = test_news.comment_set.get()
    assert comment.text == FORM_DATA['text']
    assert comment.author == reader


@pytest.mark.parametrize('incorrect_word', BAD_WORDS)
def test_correction_text_in_comment_after_creating(
    author_client,
    news_url_detail,
    test_news,
    incorrect_word,
):
    """
    Проверяет, что комментарий со стоп-словом не сохраняется
    при создании комментария.
    """
    form_data = FORM_DATA | {'text': incorrect_word}
    comments_count = test_news.comment_set.count()

    response = author_client.post(news_url_detail, data=form_data)

    form = response.context['form']

    assertFormError(form, 'text', WARNING)
    assert test_news.comment_set.count() == comments_count


@pytest.mark.parametrize('incorrect_word', BAD_WORDS)
def test_correction_text_in_comment_after_editing(
    author_client,
    comment_urls,
    test_comment,
    incorrect_word,
):
    """
    Проверяет, что комментарий со стоп-словом не сохраняется
    при редактировании комментария.
    """
    old_text = test_comment.text
    form_data = FORM_DATA | {'text': incorrect_word}

    response = author_client.post(comment_urls['url_edit'], data=form_data)

    form = response.context['form']
    assertFormError(form, 'text', WARNING)

    test_comment.refresh_from_db()
    assert test_comment.text == old_text


def test_author_can_edit_comment(
    author_client,
    comment_urls,
    test_news,
    test_comment,
):
    comments_count = test_news.comment_set.count()
    old_news = test_comment.news
    old_author = test_comment.author

    author_client.post(comment_urls['url_edit'], data=FORM_DATA)

    updated_comment = test_news.comment_set.get(pk=test_comment.pk)
    assert test_news.comment_set.count() == comments_count
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.news == old_news
    assert updated_comment.author == old_author


def test_reader_cannot_edit_comment(
    reader_client,
    comment_urls,
    test_news,
    test_comment,
):
    response = reader_client.post(comment_urls['url_edit'])

    updated_comment = test_news.comment_set.get(pk=test_comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert updated_comment.text == test_comment.text
    assert updated_comment.news == test_comment.news
    assert updated_comment.author == test_comment.author


def test_author_can_delete_comment(
    author_client,
    comment_urls,
    test_news,
    test_comment,
):
    author_client.post(comment_urls['url_delete'])

    assert not test_news.comment_set.filter(pk=test_comment.pk).exists()


def test_reader_cannot_delete_comment(
    comment_urls,
    test_news,
    test_comment,
    reader_client,
):
    response = reader_client.post(comment_urls['url_delete'])

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert test_news.comment_set.filter(pk=test_comment.pk).exists()


def test_logout_accepts_post_request(
    author_client,
    static_urls,
):

    response = author_client.post(static_urls['url_logout'])

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session
