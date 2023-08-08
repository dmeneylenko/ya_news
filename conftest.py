# conftest.py
import datetime
import pytest

from django.conf import settings
from django.utils import timezone

# Импортируем модель новости и комментария, чтобы создать экземпляр.
from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект новости.
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def all_news():
    all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=(
                      datetime.datetime.today()
                      - datetime.timedelta(days=index)
                ),
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def all_comment(author, news):
    now = timezone.now()
    for index in range(2):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(  # Создаём объект комментария.
            news=news,
            author=author,
            text=f'Текст комментария {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + datetime.timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
    return all_comment


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(  # Создаём объект комментария.
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария',
    }
