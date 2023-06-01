# news/tests/test_routes.py
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews import settings

User = get_user_model()


class TestContent(TestCase):

    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        today = datetime.today()
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='Комментатор')
        cls.reader = User.objects.create(username='Читатель простой')
        now = timezone.now()
        for index in range(2):
            cls.comment = Comment.objects.create(
                news=cls.news,
                author=cls.author,
                text=f'Текст комментария {index}'
            )
            cls.comment.created = now + timedelta(days=index)
            cls.comment.save()
        News.objects.bulk_create(
            News(title=f'Новость {index}', text='Просто текст.',
                 date=today - timedelta(days=index))
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

    def test_news_count(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = len(object_list)
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        # Получаем даты новостей в том порядке, как они выведены на странице.
        all_dates = [news.date for news in object_list]
        # Сортируем полученный список по убыванию.
        sorted_dates = sorted(all_dates, reverse=True)
        # Проверяем, что исходный список был отсортирован правильно.
        self.assertEqual(all_dates, sorted_dates)

    def test_comment_order(self):
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comments = news.comment_set.all()
        self.assertLess(all_comments[0].created, all_comments[1].created)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
