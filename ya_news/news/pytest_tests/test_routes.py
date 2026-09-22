from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'client_fixture, urls_fixture, url_name, status',
    (
        ('client', 'static_urls', 'url_home', HTTPStatus.OK),
        ('client', 'static_urls', 'url_login', HTTPStatus.OK),
        ('client', 'static_urls', 'url_signup', HTTPStatus.OK),
        ('client', 'static_urls', 'url_logout', HTTPStatus.METHOD_NOT_ALLOWED),
        ('client', 'news_url_detail', 'url_detail', HTTPStatus.OK),
        ('author_client', 'comment_urls', 'url_edit', HTTPStatus.OK),
        ('author_client', 'comment_urls', 'url_delete', HTTPStatus.OK),
        ('reader_client', 'comment_urls', 'url_delete', HTTPStatus.NOT_FOUND),
        ('reader_client', 'comment_urls', 'url_delete', HTTPStatus.NOT_FOUND),
    ),
)
def test_status_code(
    request,
    client_fixture,
    urls_fixture,
    url_name,
    status,
):
    client = request.getfixturevalue(client_fixture)
    urls = request.getfixturevalue(urls_fixture)
    response = client.get(urls[url_name])

    assert response.status_code == status


@pytest.mark.parametrize(
    'url_name',
    ('url_edit', 'url_delete'),
)
def test_anonymous_user_is_redirected_to_login(
    client,
    static_urls,
    comment_urls,
    url_name,
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
