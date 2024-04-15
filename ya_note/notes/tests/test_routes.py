from http import HTTPStatus

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

    def test_pages_availability(self):
        """
        Проверка доступности домашней страницы,
        страницы входа, выхода и регистрации.
        """
        urls = [
            ('notes:home', None, HTTPStatus.OK),  # Домашняя страница
            ('users:login', None, HTTPStatus.OK),  # Страница входа
            ('users:logout', None, HTTPStatus.OK),  # Страница выхода
            ('users:signup', None, HTTPStatus.OK),  # Страница регистрации
            ('notes:list', None, HTTPStatus.FOUND),  # Список заметок
            ('notes:add', None, HTTPStatus.FOUND),  # Добавление заметки
            ('notes:success', None, HTTPStatus.FOUND),  # Успешн добавлен замет
        ]

        for name, args, expected_status in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_availability_for_note_edit_detail_delete(self):
        """
        Проверка доступности страниц редактирования,
        детализации и удаления заметок для разных пользователей.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            urls = (
                ('edit', self.note.slug),
                ('detail', self.note.slug),
                ('delete', self.note.slug),
            )
            for name, slug in urls:
                with self.subTest(name=name, user=user):
                    url = reverse(f'notes:{name}', args=(slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

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
