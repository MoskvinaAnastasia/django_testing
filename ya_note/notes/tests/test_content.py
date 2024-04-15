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
        cls.user = User.objects.create(username='Spider-man')

    def setUp(self):
        """Настройка для каждого теста."""
        self.auth_client_reader = Client()
        self.auth_client_reader.force_login(self.reader)

        self.auth_client_author = Client()
        self.auth_client_author.force_login(self.author)

        self.user_client = Client()
        self.user_client.force_login(self.user)

        self.note_author = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author)
        self.note_reader = Note.objects.create(
            title='Заголовок Читателя',
            text='Текст Читателя',
            author=self.reader
        )
        self.url = reverse('notes:list')

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
        # Проверка формы создания заметки
        response = self.user_client.get(reverse('notes:add'))
        self.assertIsInstance(response.context['form'], NoteForm)

        # Создаем заметку для тестирования формы редактирования
        note = Note.objects.create(
            title='Fighting Otto Octaviuse',
            text='More tentacles',
            author=self.user
        )

        # Проверка формы редактирования заметки
        response = self.user_client.get(
            reverse('notes:edit', args=[note.slug]))
        self.assertIsInstance(response.context['form'], NoteForm)
