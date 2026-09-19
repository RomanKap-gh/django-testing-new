from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING


FORM_DATA = {
    'text': 'Новый текст',
}


def test_creating_comment_is_unavailable_to_anonymous_user(
    news_url,
    client,
    test_news,
):
    comments_before = set(test_news.comment_set.values_list('pk', flat=True))
    response = client.post(news_url['url_detail'], data=FORM_DATA)
    comments_after = set(test_news.comment_set.values_list('pk', flat=True))

    assert response.status_code == HTTPStatus.FOUND
    assert comments_after == comments_before


def test_success_creating_comment_by_authenticated_user(
    news_url,
    reader_client,
    reader,
    test_news,
):
    response = reader_client.post(news_url['url_detail'], data=FORM_DATA)

    assert response.status_code == 302
    assert response.url == news_url['url_detail'] + '#comments'
    assert test_news.comment_set.count() == 1
    comment = test_news.comment_set.get()
    assert comment.text == FORM_DATA['text']
    assert comment.author == reader


def test_success_redirect_after_edit_comment(
    news_url,
    comment_urls,
    author_client,
):
    response = author_client.post(comment_urls['url_edit'], data=FORM_DATA)

    assert response.url == news_url['url_detail'] + '#comments'


def test_success_redirect_after_delete_comment(
    news_url,
    comment_urls,
    author_client,
):
    response = author_client.post(comment_urls['url_delete'])

    assert response.url == news_url['url_detail'] + '#comments'


@pytest.mark.parametrize('incorrect_word', BAD_WORDS)
def test_correction_text_in_comment_after_creating(
    news_url,
    author_client,
    test_news,
    incorrect_word,
):
    form_data = FORM_DATA | {'text': incorrect_word}
    comments_count = test_news.comment_set.count()

    response = author_client.post(news_url['url_detail'], data=form_data)

    form = response.context['form']

    assert form.errors['text'] == [WARNING]
    assert test_news.comment_set.count() == comments_count


@pytest.mark.parametrize('incorrect_word', BAD_WORDS)
def test_correction_text_in_comment_after_editing(
    comment_urls,
    author_client,
    incorrect_word,
):
    form_data = FORM_DATA | {'text': incorrect_word}

    response = author_client.post(comment_urls['url_edit'], data=form_data)

    form = response.context['form']

    assert form.errors['text'] == [WARNING]


def test_author_can_edit_comment(
    news_url,
    comment_urls,
    test_news,
    test_comment,
    author_client
):
    comments_count = test_news.comment_set.count()
    old_news = test_comment.news
    old_author = test_comment.author

    response = author_client.post(comment_urls['url_edit'], data=FORM_DATA)

    updated_comment = test_news.comment_set.get(pk=test_comment.pk)
    assert response.url == news_url['url_detail'] + '#comments'
    assert test_news.comment_set.count() == comments_count
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.news == old_news
    assert updated_comment.author == old_author


def test_reader_cannot_edit_comment(
    comment_urls,
    test_news,
    test_comment,
    reader_client
):
    response = reader_client.post(comment_urls['url_edit'])

    updated_comment = test_news.comment_set.get(pk=test_comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert updated_comment.text == test_comment.text
    assert updated_comment.news == test_comment.news
    assert updated_comment.author == test_comment.author


def test_author_can_delete_comment(
    news_url,
    comment_urls,
    test_news,
    test_comment,
    author_client,
):
    response = author_client.post(comment_urls['url_delete'])

    assert response.url == news_url['url_detail'] + '#comments'
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
