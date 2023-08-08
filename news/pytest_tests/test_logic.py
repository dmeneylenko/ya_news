import pytest

from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize(
    # parametrized_client - название параметра,
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    'parametrized_client, comments_count',
    # В кортеже с кортежами передаём значения для параметров:
    (
        (pytest.lazy_fixture('admin_client'), 1),
        (pytest.lazy_fixture('client'), 0)
    ),
)
def test_user_cant_create_comment(
    parametrized_client,
    news,
    form_data,
    comments_count
):
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.
    url = reverse('news:detail', args=(news.id,))
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    parametrized_client.post(url, data=form_data)
    assert Comment.objects.count() == comments_count


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, news, form_data):
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] = bad_words_data
    response = admin_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(response, 'form', 'text', errors=(WARNING))
    # Дополнительно убедимся, что комментарий не был создан.
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, comment, news):
    # Получаем адрес страницы редактирования комментария:
    url = reverse('news:edit', args=(comment.id,))
    # В POST-запросе на адрес редактирования комментария
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(url, form_data)
    # Проверяем редирект:
    assertRedirects(response, reverse(
        'news:detail',
        args=(news.id,))+'#comments'
    )
    # Обновляем объект заметки note: получаем обновлённые данные из БД:
    comment.refresh_from_db()
    # Проверяем, что атрибуты коментария соответствуют обновлённым:
    assert comment.text == form_data['text']


def test_other_user_can_edit_comment(admin_client, form_data, comment):
    # Получаем адрес страницы редактирования комментария:
    url = reverse('news:edit', args=(comment.id,))
    # В POST-запросе на адрес редактирования комментария
    # отправляем form_data - новые значения для полей заметки:
    response = admin_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(id=comment.id)
    # Проверяем, что атрибуты объекта из БД равны
    # атрибутам коммента до запроса.
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, comment, news):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(response, reverse(
        'news:detail',
        args=(news.id,))+'#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
