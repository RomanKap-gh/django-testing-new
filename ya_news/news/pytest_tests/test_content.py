from django.urls import reverse

from news.pytest_tests.conftest import NOTES_ON_PAGE
from news.forms import CommentForm


def test_news_are_sorted_newest_first(
    many_test_news,
    author_client,
):
    response = author_client.get(reverse('news:home'))
    object_list = list(response.context['object_list'])
    expected_news = list(reversed(many_test_news))[:NOTES_ON_PAGE]

    assert object_list == expected_news


def test_news_count_on_page_is_limited(
    many_test_news,
    author_client,
):
    response = author_client.get(reverse('news:home'))
    object_list = response.context['object_list']

    assert len(object_list) == NOTES_ON_PAGE


def test_comments_are_sorted_oldest_first(
    news_url,
    test_comments,
    author_client,
):
    response = author_client.get(news_url['url_detail'])
    news = response.context['object']
    comments_list = list(news.comment_set.all())
    expected_comments_list = list(test_comments)

    assert comments_list == expected_comments_list


def test_form_is_unavailable_to_anonymous_user(
    news_url,
    client,
):
    response = client.get(news_url['url_detail'])

    assert response.status_code == 200
    assert 'form' not in response.context


def test_form_is_available_to_authenticated_user(
    news_url,
    author_client,
):
    response = author_client.get(news_url['url_detail'])

    assert response.status_code == 200
    assert isinstance(response.context['form'], CommentForm)
