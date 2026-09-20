from datetime import date, datetime, timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

NOTES_ON_PAGE = 10
COUNT_COMMENTS = 5


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def test_news(author, db):
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
        date=date(2026, 10, 14)
    )


@pytest.fixture
def test_comment(test_news, author):
    return Comment.objects.create(
        news=test_news,
        text='Текст тестового комментария',
        author=author,
    )


@pytest.fixture
def many_test_news(author, db):
    return News.objects.bulk_create(
        [
            News(
                title=f'Тестовая новость {index}',
                text='Текст тестовой новости',
                date=date(2026, 10, index),
            )
            for index in range(1, NOTES_ON_PAGE + 2)
        ]
    )


@pytest.fixture
def test_comments(test_news, author, db):
    start = timezone.make_aware(datetime(2026, 11, 1, 12, 0, 0))
    comments = []
    for index in range(COUNT_COMMENTS):
        comment = Comment.objects.create(
            news=test_news,
            text=f'Текст тестового комментария {index}',
            author=author,
        )
        created = start + timedelta(minutes=index)
        Comment.objects.filter(pk=comment.pk).update(created=created)
        comment.created = created
        comments.append(comment)
    return comments


@pytest.fixture
def news_url_detail(test_news):
    return reverse("news:detail", kwargs={"pk": test_news.pk})


@pytest.fixture
def comment_urls(test_comment):
    return {
        'url_edit': reverse('news:edit', kwargs={'pk': test_comment.pk}),
        'url_delete': reverse('news:delete', kwargs={'pk': test_comment.pk}),
    }


@pytest.fixture
def static_urls():
    return {
        'url_home': reverse('news:home'),
        'url_login': reverse('users:login'),
        'url_logout': reverse('users:logout'),
        'url_signup': reverse('users:signup'),
    }
