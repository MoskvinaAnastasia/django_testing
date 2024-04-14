from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
import pytest

from news.models import Comment, News


@pytest.fixture
def parametrized_client(author_client, anonymous_client):
    return {'author_client': author_client,
            'anonymous_client': anonymous_client}


@pytest.fixture
# Используем встроенную фикстуру модели пользователей
# для создания пользователя - Автор.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
# Используем встроенную фикстуру модели пользователей
# для создания пользователя - Не автор.
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не Автор')


@pytest.fixture
# Создаем клиента Автора.
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
# Создаем клиента не Автора.
def not_author_client(not_author):  # Вызываем фикстуру не автора.
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
# Создаём анонимного клиента.
def anonymous_client():
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    return client


@pytest.fixture
# Создаём объект новости.
def news(author):
    news = News.objects.create(
        title='Заголовок новости',
        text='ТекстВ',
    )
    return news


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания новости.
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
# Создаём объект комментарий.
def comment(author, news):
    comment = Comment.objects.create(  # Создаём объект комментария.
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания комментария новости.
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
# Адрес страницы новости.
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
# Создаём список новостей.
def list_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новая новость {index}',
            text='Ляляля.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
# Создаём список комментариев.
def list_comment(author, news):
    today = datetime.today()
    all_comments = [
        Comment(
            news=news,
            author=author,
            text='Текст комментария',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            created=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    Comment.objects.bulk_create(all_comments)


@pytest.fixture
# Словарь формы для создания тестового комментария.
def comment_form_data(author, news):
    return {
        'news': news,
        'author': author,
        'text': 'Новый текст',
    }


@pytest.fixture
# Адрес страницы удаления комментария.
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
# Адрес страницы для редактирования комментария.
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
# Адрес страницы комментариев новости.
def comments_url(detail_url):
    return detail_url + '#comments'
