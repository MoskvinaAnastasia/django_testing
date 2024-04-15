from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteOperations(TestCase):
    """Набор тестов для проверки операций над заметками."""

    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок'
    NEW_NOTE_TEXT = 'Новый текст заметки'
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
        cls.url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.reader = User.objects.create(username='Раст')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_data = {
            'title': cls.NEW_NOTE_TITLE, 'text': cls.NEW_NOTE_TEXT
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверка, что анонимный пользователь не может создать заметку."""
        initial_notes_count = Note.objects.count()
        self.client.post(
            self.url, data={'title': self.NOTE_TITLE, 'text': self.NOTE_TEXT})
        notes_count = Note.objects.count()
        self.assertEqual(initial_notes_count, notes_count)

    def test_user_can_create_note(self):
        """Проверка, что авторизованный пользователь может создать заметку."""
        initial_notes_count = Note.objects.count()
        response = self.author_client.post(
            self.url, data={'title': self.NEW_NOTE_TITLE,
                            'text': self.NOTE_TEXT})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(initial_notes_count + 1, notes_count)
        self.assertTrue(Note.objects.filter(
            title=self.NEW_NOTE_TITLE, text=self.NOTE_TEXT).exists())

    def test_slug_generation(self):
        """Проверка генерации slug."""
        note_slug = slugify(self.NOTE_TITLE)
        self.assertEqual(self.note.slug, note_slug)

    def test_non_unique_slug_validation(self):
        """
        Проверка, что невозможно создать
        две заметки с одинаковым slug.
        """
        form_data = {
            'title': 'Вторая заметка',
            'text': 'Текст второй заметки',
            'slug': slugify(self.note.title),
        }
        response = self.author_client.post(self.url, data=form_data)
        self.assertFormError(
            response, 'form', 'slug', form_data['slug'] + WARNING)

    def test_user_can_edit_own_note(self):
        """Пользователь может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.edit_data)
        self.assertRedirects(response, reverse('notes:success'))
        edited_note = Note.objects.get(pk=self.note.id)
        self.assertEqual(edited_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(edited_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(edited_note.author, self.author)
        self.assertEqual(edited_note.slug, slugify(self.NEW_NOTE_TITLE))

    def test_user_cant_edit_other_users_note(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.edit_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        old_title = self.note.title
        old_text = self.note.text
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, old_title)
        self.assertEqual(self.note.text, old_text)

    def test_user_can_delete_own_note(self):
        """Пользователь может удалить свою заметку."""
        initial_notes_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_notes_count - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cant_delete_other_users_note(self):
        """Пользователь не может удалить чужую заметку."""
        initial_notes_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_notes_count)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
