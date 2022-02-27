from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from apps.feed.models import Feed
from apps.feed.models import Reader
from apps.feed.tests.factories import FeedFactory
from apps.feed.tests.factories import FeedItemFactory
from apps.feed.tests.factories import ReaderFactory


class BaseViewSetTestMixin:
    def setUp(self) -> None:
        self.login_url: str = reverse('accounts-login')
        self.feed_item_user_url: str = reverse('feed-item-list')
        self.feed_url: str = reverse('feed-list')


class ReaderViewSetTest(BaseViewSetTestMixin, APITestCase):

    def test_user_reader_feed(self) -> None:
        request: APIClient = self.client

        feed_items: list = FeedItemFactory.create_batch(2)
        readers = ReaderFactory.create_batch(1)  # will create a user
        user: User = readers[0].user
        # Add feed_items to reader
        # query db to check
        reader: Reader = Reader.objects.get(user=user)
        # Add items to reader
        for item in feed_items:
            reader.items.add(item)
        reader.save()
        # Login User Reader
        # Update user password
        user: User = User.objects.get(username=user.username)
        user.set_password('password')
        user.save()
        response = request.post(
            self.login_url, {
                'username': user.username, 'password': 'password',
            },
        )
        token = response.json()['token']
        response = request.get(self.feed_item_user_url)
        self.assertEqual(response.status_code, 401)
        request.credentials(HTTP_AUTHORIZATION='Token ' + token)
        # Create another batch
        FeedItemFactory.create_batch(2)
        response = request.get(self.feed_item_user_url)
        self.assertEqual(response.json()['count'], 4)
        response = request.get(
            self.feed_item_user_url
            + '?read=True', )  # List all read items
        self.assertEqual(response.json()['count'], 2)


class SubscribeViewSetTest(BaseViewSetTestMixin, APITestCase):

    def test_user_subscribe_feed(self) -> None:
        request: APIClient = self.client

        feed: list = FeedFactory.create_batch(1)
        user: User = User.objects.get(username=feed[0].user.username)
        user.set_password('hello')
        user.save()
        response = request.post(
            self.login_url, {
                'username': user.username, 'password': 'hello',
            },
        )
        token = response.json()['token']
        user_feed = Feed.objects.filter(user=user)
        self.assertEqual(user_feed.count(), 1)
        request.credentials(HTTP_AUTHORIZATION='Token ' + token)
        # Create another batch
        response = request.get(self.feed_url)
        self.assertEqual(response.json()['count'], 1)
        response = request.get(self.feed_url + '?subscribed=True')
        self.assertEqual(response.json()['count'], 0)
