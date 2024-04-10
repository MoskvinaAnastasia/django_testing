# Импортируем функцию для получения модели пользователя.
from django.contrib.auth import get_user_model
# Импортируем настройки проекта, чтобы получить доступ к парамеру пагинации.
from django.conf import settings
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
# Импортируем класс формы.
from news.forms import CommentForm
# Импортируем библиотеку pytest.
import pytest

# Получаем модель пользователя.
User = get_user_model()

# Задаем адрес домашней страницы в качестве глобальной константы.
HOME_URL = reverse('news:home')


@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, form_in_context',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('anonymous_client'), False),
    )
)
def test_different_user_has_or_not_form(
        parametrized_client,
        detail_url,
        form_in_context,
):
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is form_in_context
    if form_in_context:
        assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_news_count(client, list_news):
    # Загружаем главную страницу.
    response = client.get(HOME_URL)
    # Код ответа не проверяем, его уже проверили в тестах маршрутов.
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    news_count = object_list.count()
    # Проверяем, что на странице именно 10 новостей.
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


def test_comments_order(
        client, news, list_comment, detail_url
):
    response = client.get(detail_url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    # Получаем объект новости.
    news = response.context['news']
    print(news)
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    # # Собираем временные метки всех новостей.
    all_timestamps = [comment.created for comment in all_comments]
    # # Сортируем временные метки, менять порядок сортировки не надо.
    sorted_timestamps = sorted(all_timestamps)
    # # Проверяем, что id первого комментария меньше id второго.
    assert all_timestamps == sorted_timestamps
