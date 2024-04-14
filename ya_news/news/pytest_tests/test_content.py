from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm
import pytest

# Получаем модель пользователя.
User = get_user_model()

# Задаем адрес домашней страницы в качестве глобальной константы.
HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_logged_in_user_has_comment_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


# Тест для анонимного пользователя
def test_anonymous_user_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_news_count(client, list_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(
        client, news, list_comment, detail_url
):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
