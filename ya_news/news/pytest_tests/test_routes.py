from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.pytest_tests.test_logic import FORM_DATA


@pytest.mark.parametrize(
    'url_name',
    ('url_home', 'url_login', 'url_signup'),
)
def test_public_static_pages_are_available(client, static_urls, url_name):

    response = client.get(static_urls[url_name])

    assert response.status_code == HTTPStatus.OK


def test_public_page_detail_is_available(client, news_url_detail):

    response = client.get(news_url_detail)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    ('url_edit', 'url_delete'),
)
def test_pages_edit_and_delete_are_available_to_author(
    comment_urls,
    author_client,
    url_name,
):

    response = author_client.get(comment_urls[url_name])

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    ('url_edit', 'url_delete'),
)
def test_pages_edit_and_delete_are_unavailable_to_reader(
    comment_urls,
    reader_client,
    url_name
):

    response = reader_client.get(comment_urls[url_name])

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_name',
    ('url_edit', 'url_delete'),
)
def test_anonymous_user_is_redirected_to_login(
    comment_urls,
    client,
    url_name,
    static_urls,
):
    login_url = static_urls['url_login']

    expected_url = f'{login_url}?next={comment_urls[url_name]}'

    response = client.get(comment_urls[url_name])

    assertRedirects(response, expected_url)


def test_logout_accepts_post_request(
    author_client,
    static_urls,
):

    response = author_client.post(static_urls['url_logout'])

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session


def test_logout_rejects_get_request(
    client,
    static_urls,
):

    response = client.get(static_urls['url_logout'])

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_success_redirect_after_edit_comment(
    news_url_detail,
    comment_urls,
    author_client,
):
    response = author_client.post(comment_urls['url_edit'], data=FORM_DATA)

    assert response.url == news_url_detail + '#comments'


def test_success_redirect_after_delete_comment(
    news_url_detail,
    comment_urls,
    author_client,
):
    response = author_client.post(comment_urls['url_delete'])

    assert response.url == news_url_detail + '#comments'
