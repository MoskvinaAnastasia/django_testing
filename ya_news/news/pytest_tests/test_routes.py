import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability(
        client,
        name,
        args,
):
    """Проверка доступности страниц по их именам."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    ),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client,
        name,
        args,
        expected_status,
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    # Устанавливаем адрес страницы переадресации
    login_url = reverse('users:login')
    # Формируем адрес страницы обращения.
    url = reverse(name, args=args)
    # Устанавливаем адрес на которой должен попасть
    # пользователь после авторизации.
    expected_url = f'{login_url}?next={url}'
    # Загружаем страницу.
    response = client.get(url)
    # Проверяем переадресацию.
    assertRedirects(response, expected_url)
