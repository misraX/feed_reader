from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from apps.feed.models import Reader
from apps.feed.tests.factories import FeedItemFactory
from apps.feed.tests.factories import ReaderFactory


class ReaderViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.login_url: str = reverse('accounts-login')
        self.feed_item_user_url: str = reverse('feed-item-list')

    def test_user_reader_feed(self) -> None:
        request: APIClient = self.client

        feed_items = FeedItemFactory.create_batch(2)
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
        request.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = request.get(self.feed_item_user_url)
        print(response.json())
