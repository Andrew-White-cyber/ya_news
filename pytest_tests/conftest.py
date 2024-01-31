import pytest
from datetime import datetime, timedelta
from django.utils import timezone
# Импортируем класс клиента.
from django.test.client import Client
from django.conf import settings
# Импортируем модель новости, чтобы создать экземпляр.
from news.models import News, Comment




@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news(db):
    news = News.objects.create(  # Создаём объект новости.
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def all_news(db):
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)  # Для каждой новости уменьшаем дату на index дней, index - счётчик цикла.
        )
        all_news.append(news)
    return all_news

@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def add_two_comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()


@pytest.fixture
def id_for_args(comment):
    return (comment.id,)


# Добавляем фикстуру form_data
@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }

@pytest.fixture
def updated_form_data():
    return {
        'text': 'Updated text'
    }

@pytest.fixture
def bad_words():
    return (
     'редиска',
     'негодяй',
    )
