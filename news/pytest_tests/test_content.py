import pytest
from django.urls import reverse
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


HOME_URL = reverse('news:home')


@pytest.mark.django_db
@pytest.mark.parametrize(
        'user_client, has_form',
        [
            (pytest.lazy_fixture('client'), False),
            (pytest.lazy_fixture('author_client'), True)
        ]
)
def test_comment_form(user_client, has_form, news, detail_url):
    response = user_client.get(detail_url)
    assert ('form' in response.context) is has_form


@pytest.mark.django_db
def test_news_count(all_news, client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(all_news, client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    for index in range(len(object_list)-1):
        assert object_list[index].date > object_list[index+1].date


@pytest.mark.django_db
def test_comments_order(news, comment, another_comment, client, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created
