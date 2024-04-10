from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteContent(TestCase):
    """Набор тестов для проверки контента создания заметок."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.reader = User.objects.create(username='reader')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.reader)
        cls.author = User.objects.create(username='author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note_author = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author)
        cls.note_reader = Note.objects.create(
            title='Заголовок Читателя',
            text='Текст Читателя',
            author=cls.reader
        )
        cls.url = reverse('notes:list')

    def test_note_is_not_in_object_list_for_another_user(self):
        """
        Проверка, что в список заметок одного пользователя не
        попадают заметки другого пользователя.
        """
        user = self.reader
        self.client.force_login(user)
        response = self.client.get(self.url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note_author, object_list)

    def test_single_note_in_object_list(self):
        """
        Проверка, что отдельная заметка передается
        на страницу со списком заметок
        в списке object_list в словаре context.
        """
        user = self.reader
        self.client.force_login(user)
        response = self.client.get(self.url)
        object_list = response.context['object_list']
        self.assertIn(self.note_reader, object_list)


class TestNoteForms(TestCase):
    """Набор тестов для проверки форм создания и редактирования заметок."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.user = User.objects.create(username='Spider-man')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_note_create_form_is_passed_to_create_page(self):
        """
        Проверка, что форма создания заметки
        передается на страницу создания.
        """
        response = self.user_client.get(reverse('notes:add'))
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_update_form_is_passed_to_update_page(self):
        """
        Проверка, что форма редактирования заметки
        передается на страницу редактирования.
        """
        note = Note.objects.create(
            title='Fighting Otto Octaviuse',
            text='More tentacles',
            author=self.user)
        response = self.user_client.get(
            reverse('notes:edit', args=[note.slug]))
        self.assertIsInstance(response.context['form'], NoteForm)
