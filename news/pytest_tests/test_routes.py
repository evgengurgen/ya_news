from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    ]
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args'))
     ]
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
        'user_client, expected_status',
        [
            (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
        ]
)
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args'))
     ]
)
def test_availability_for_comment_edit_and_delete(user_client, name, args,
                                                  expected_status):
    url = reverse(name, args=args)
    response = user_client.get(url)
    assert response.status_code == expected_status
