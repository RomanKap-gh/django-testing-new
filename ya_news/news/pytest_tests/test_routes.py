from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup'),
)
def test_public_pages_are_available(client, name, db):
    url = reverse(name)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_public_page_detail_is_available(client, news_url):

    response = client.get(news_url['url_detail'])

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
):
    login_url = reverse('users:login')

    expected_url = f'{login_url}?next={comment_urls[url_name]}'

    response = client.get(comment_urls[url_name])

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


def test_logout_accepts_post_request(
    author_client,
):

    response = author_client.post(reverse('users:logout'))

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session


def test_logout_rejects_get_request(client):

    response = client.get(reverse('users:logout'))

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
