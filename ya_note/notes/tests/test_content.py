from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteContentAndForms(TestCase):
    """Набор тестов для проверки контента создания заметок
    и форм создания и редактирования заметок.
    """

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')

        cls.auth_client_reader = Client()
        cls.auth_client_reader.force_login(cls.reader)

        cls.auth_client_author = Client()
        cls.auth_client_author.force_login(cls.author)

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
        response = self.auth_client_reader.get(self.url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note_author, object_list)

    def test_single_note_in_object_list(self):
        """
        Проверка, что отдельная заметка передается
        на страницу со списком заметок
        в списке object_list в словаре context.
        """
        response = self.auth_client_reader.get(self.url)
        object_list = response.context['object_list']
        self.assertIn(self.note_reader, object_list)

    def test_note_forms_are_passed_to_pages(self):
        """
        Проверка, что форма создания заметки передается
        на страницу создания, и что форма редактирования заметки
        передается на страницу редактирования.
        """
        urls = [
            ('notes:add', None),
            ('notes:edit', self.note_author.slug)
        ]

        for name, slug in urls:
            with self.subTest(name=name):
                url = reverse(name, args=[slug]) if slug else reverse(name)
                response = self.auth_client_author.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
