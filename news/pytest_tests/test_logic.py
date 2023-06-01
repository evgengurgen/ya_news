from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING


def test_user_can_create_comments(author_client, author,
                                  form_data, detail_url):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comments(client, form_data, detail_url):
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news, bad_form_data,
                                 detail_url):
    response = author_client.post(detail_url, data=bad_form_data)
    assertFormError(response,
                    form='form',
                    field='text',
                    errors=WARNING
                    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, news, comment,
                                   comment_id_for_args, detail_url):
    url = reverse('news:delete', args=comment_id_for_args)
    url_to_comments = detail_url + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(admin_client, news, comment,
                                        comment_id_for_args):
    url = reverse('news:delete', args=comment_id_for_args)
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, news,
                                 comment, comment_id_for_args,
                                 detail_url, new_form_data):
    url = reverse('news:edit', args=comment_id_for_args)
    url_to_comments = detail_url + '#comments'
    response = author_client.post(url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_form_data['text']


def test_other_user_cant_edit_comment(admin_client, news,
                                      comment, comment_id_for_args,
                                      detail_url, new_form_data):
    url = reverse('news:edit', args=comment_id_for_args)
    ORIGINAL_COMMENT = comment.text
    response = admin_client.post(url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == ORIGINAL_COMMENT
