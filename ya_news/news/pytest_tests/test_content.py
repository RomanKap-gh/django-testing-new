from http import HTTPStatus

from news.forms import CommentForm
from news.models import Comment, News
from news.pytest_tests.conftest import NOTES_ON_PAGE


def test_news_are_sorted_newest_first(
    many_test_news,
    author_client,
    static_urls,
):
    response = author_client.get(static_urls['url_home'])
    object_list = list(response.context['object_list'])
    expected_news = list(News.objects.order_by('-date'))[:NOTES_ON_PAGE]

    assert object_list == expected_news


def test_news_count_on_page_is_limited(
    many_test_news,
    author_client,
    static_urls,
):
    response = author_client.get(static_urls['url_home'])
    object_list = response.context['object_list']

    assert object_list.count() == NOTES_ON_PAGE


def test_comments_are_sorted_oldest_first(
    news_url_detail,
    test_news,
    test_comments,
    author_client,
):
    response = author_client.get(news_url_detail['url_detail'])
    news = response.context['object']
    comments_list = list(news.comment_set.all())
    expected_comments_list = list(
        Comment.objects.filter(news=test_news).order_by('created')
    )

    assert comments_list == expected_comments_list


def test_form_is_unavailable_to_anonymous_user(
    news_url_detail,
    client,
):
    response = client.get(news_url_detail['url_detail'])

    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_form_is_available_to_authenticated_user(
    news_url_detail,
    author_client,
):
    response = author_client.get(news_url_detail['url_detail'])

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context['form'], CommentForm)
