from http import HTTPStatus

from django.test import Client
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Набор тестов для проверки маршрутов адресов заметок."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.author = User.objects.create(username='Раст')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.reader = User.objects.create(username='Марти')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_route_accessibility(self):
        """Проверка доступности страниц для разных пользователей."""
        urls = [
            ('notes:home', self.client, HTTPStatus.OK, None),
            ('users:login', self.client, HTTPStatus.OK, None),
            ('users:logout', self.client, HTTPStatus.OK, None),
            ('users:signup', self.client, HTTPStatus.OK, None),
            ('notes:list', self.client, HTTPStatus.FOUND, None),
            ('notes:add', self.client, HTTPStatus.FOUND, None),
            ('notes:success', self.client, HTTPStatus.FOUND, None),
            ('notes:edit', self.author_client,
             HTTPStatus.OK, (self.note.slug,)),
            ('notes:detail', self.client, HTTPStatus.FOUND, (self.note.slug,)),
            ('notes:delete', self.author_client,
             HTTPStatus.OK, (self.note.slug,)),
            ('notes:delete', self.reader_client,
             HTTPStatus.NOT_FOUND, (self.note.slug,)),
            ('notes:edit', self.reader_client,
             HTTPStatus.NOT_FOUND, (self.note.slug,)),
        ]

        for name, client, expected_status, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверка перенаправления для анонимных клиентов
        для различных маршрутов.
        """
        login_url = reverse('users:login')
        urls = [
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None)
        ]

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
