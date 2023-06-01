import pytest

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from django.utils import timezone
from datetime import datetime, timedelta
from django.urls import reverse
from news.forms import BAD_WORDS


now = timezone.now()
today = datetime.today()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def all_news():
    News.objects.bulk_create(
            News(title=f'Новость {index+1}', text='Просто текст.',
                 date=today - timedelta(days=index))
            for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
        )


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )
    return comment


@pytest.fixture
def another_comment(news, author):
    another_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Другой текст'
    )
    another_comment.created = now + timedelta(days=1)
    another_comment.save()
    return another_comment


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def detail_url(news):
    url = reverse('news:detail', args=(news.id,))
    return url


@pytest.fixture
def form_data():
    return {
        'text': 'Комментарий'
    }


@pytest.fixture
def bad_form_data():
    return {
        'text': 'Комментарий ' + BAD_WORDS[0]
    }


@pytest.fixture
def new_form_data():
    return {
        'text': 'Новый комментарий'
    }
