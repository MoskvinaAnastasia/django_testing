from http import HTTPStatus

from django.urls import reverse
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_client, url, status',
    (
        (pytest.lazy_fixture('anonymous_client'),
         reverse('news:home'), HTTPStatus.OK),
        (pytest.lazy_fixture('anonymous_client'),
         pytest.lazy_fixture('detail_url'), HTTPStatus.OK),
        (pytest.lazy_fixture('anonymous_client'),
         reverse('users:login'), HTTPStatus.OK),
        (pytest.lazy_fixture('anonymous_client'),
         reverse('users:logout'), HTTPStatus.OK),
        (pytest.lazy_fixture('anonymous_client'),
         reverse('users:signup'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'),
         pytest.lazy_fixture('comment_edit_url'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('not_author_client'),
         pytest.lazy_fixture('comment_delete_url'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'),
         pytest.lazy_fixture('comment_edit_url'), HTTPStatus.OK),
        (pytest.lazy_fixture('author_client'),
         pytest.lazy_fixture('comment_delete_url'), HTTPStatus.OK),
    ),
)
def test_pages_availability(
        user_client,
        url,
        status,
):
    """Проверка доступности страниц по их
    именам для анонимных пользователей.
    """
    response = user_client.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('comment_edit_url'),
        pytest.lazy_fixture('comment_delete_url'),
    ),
)
def test_pages_redirect_for_anonymous_users(
        anonymous_client,
        url,
):
    """Проверка перенаправления страниц для анонимных пользователей."""
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = anonymous_client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url
