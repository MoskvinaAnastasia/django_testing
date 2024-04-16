import pytest
from django.urls import reverse
from http import HTTPStatus


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, expected_status',
    (
        ('news:home', None, HTTPStatus.OK),
        ('news:detail',
            pytest.lazy_fixture('news_id_for_args'), HTTPStatus.OK),
        ('users:login', None, HTTPStatus.OK),
        ('users:logout', None, HTTPStatus.OK),
        ('users:signup', None, HTTPStatus.OK),
        ('news:edit',
            pytest.lazy_fixture('comment_id_for_args'), HTTPStatus.NOT_FOUND),
        ('news:delete',
            pytest.lazy_fixture('comment_id_for_args'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_and_redirect(
        client,
        name,
        args,
        expected_status,
):
    """
    Проверка доступности страниц по их именам и
    перенаправления для анонимных пользователей.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    if expected_status == HTTPStatus.OK:
        # Проверка доступности страницы для анонимных пользователей
        assert response.status_code == HTTPStatus.OK
    else:
        # Проверка перенаправления для анонимных пользователей
        login_url = reverse('users:login')
        expected_redirect_url = f'{login_url}?next={url}'
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == expected_redirect_url
