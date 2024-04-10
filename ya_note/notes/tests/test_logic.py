from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm, WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteLogic(TestCase):
    """Набор тестов для проверки логики создания заметок."""
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.author = User.objects.create(username='Марти')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url = reverse('notes:add')
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT}

    def test_anonymous_user_cant_create_note(self):
        """Проверка, что анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Проверка, что авторизованный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(response.url, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_unique_slug(self):
        """Проверка, что создается уникальный slug при создании заметки."""
        form_data = {
            'title': 'Заголовок без slug', 'text': 'Текст заметки без slug'
        }
        form = NoteForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['slug'], slugify(form_data['title'])
        )

    def test_non_unique_slug_validation(self):
        """
        Проверка, что невозможно создать
        две заметки с одинаковым slug.
        """
        # Создаем первую заметку
        note_slug_1 = 'pervaya-zametka'
        Note.objects.create(
            title='Первая заметка',
            text='Текст первой заметки',
            slug=note_slug_1,
            author=self.author
        )

        # Отправляем запрос на создание второй заметки с тем же слагом
        response = self.auth_client.post(self.url, data={
            'title': 'Вторая заметка',
            'text': 'Текст второй заметки',
            'slug': note_slug_1,
        })

        # Проверяем, что запрос вернул ошибку
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, WARNING)


class TestNoteEditDelete(TestCase):
    """
    Набор тестов для проверки редактирования
    и удаления заметок автором/не автором.
    """

    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NOTE_TITLE = 'Заголовок'
    NEW_NOTE_TITLE = 'Новый Заголовок'

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов."""
        cls.author = User.objects.create(username='Марти')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.reader = User.objects.create(username='Раст')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_data = {
            'title': cls.NEW_NOTE_TITLE, 'text': cls.NEW_NOTE_TEXT
        }

    def test_user_can_edit_own_note(self):
        """Пользователь может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.edit_data)
        self.assertRedirects(response, reverse('notes:success'))
        edited_note = Note.objects.get(pk=self.note.id)
        self.assertEqual(edited_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(edited_note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_other_users_note(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.edit_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_can_delete_own_note(self):
        """Пользователь может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_other_users_note(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
