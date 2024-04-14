from http import HTTPStatus
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertRedirects, assertFormError


def test_anonymous_user_cant_create_comment(
        anonymous_client,
        comment_form_data,
        detail_url,
):
    """Проверяем, что анонимный пользователь не может создать комментарий."""
    initial_comments_count = Comment.objects.count()
    anonymous_client.post(detail_url, data=comment_form_data)
    final_comments_count = Comment.objects.count()
    assert final_comments_count == initial_comments_count


def test_user_can_create_comment(
        author,
        author_client,
        detail_url,
        comment_form_data,
        news,
):
    """Проверяем, что пользователь может создать комментарий."""
    initial_comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=comment_form_data)
    assertRedirects(response, f'{detail_url}#comments')
    final_comments_count = Comment.objects.count()
    assert final_comments_count == initial_comments_count + 1
    created_comment = Comment.objects.last()
    assert created_comment.text == comment_form_data['text']
    assert created_comment.news == news
    assert created_comment.author == author


def test_user_cant_use_bad_words(
        author_client,
        detail_url,
):
    """Проверяем, что пользователь не может использовать
    запрещенные слова в комментариях.
    """
    initial_comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, еще немного текста'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    final_comments_count = Comment.objects.count()
    assert final_comments_count == initial_comments_count


def test_author_can_delete_comment(
        author_client,
        comment,
        comment_delete_url,
        comments_url,
):
    """Проверяем, что автор комментария может удалить свой комментарий."""
    initial_comments_count = Comment.objects.count()
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, comments_url)
    assert response.status_code == HTTPStatus.FOUND
    final_comments_count = Comment.objects.count()
    assert final_comments_count == initial_comments_count - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_user_cant_delete_comment_of_another_user(
        comment,
        comment_delete_url,
        not_author_client,
):
    """Проверяем, что пользователь не может удалить
    комментарий другого пользователя.
    """
    initial_comments_count = Comment.objects.count()
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    final_comments_count = Comment.objects.count()
    assert final_comments_count == initial_comments_count
    assert Comment.objects.filter(pk=comment.id).exists()


def test_author_can_edit_comment(
        author_client,
        comment,
        comment_edit_url,
        comment_form_data,
        comments_url,
):
    """Проверяем, что автор комментария может
    отредактировать свой комментарий.
    """
    response = author_client.post(comment_edit_url, data=comment_form_data)
    assertRedirects(response, comments_url)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']
    assert comment.author == comment.author
    assert comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment,
        comment_edit_url,
        comment_form_data,
):
    """Проверяем, что пользователь не может редактировать
    комментарий другого пользователя.
    """
    response = not_author_client.post(comment_edit_url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != comment_form_data['text']
    assert comment.author == comment.author
    assert comment.created == comment.created
