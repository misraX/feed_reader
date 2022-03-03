from django.test.utils import override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.feed.models import DONE
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader
from apps.feed.tasks import update_all_feeds
from apps.feed.tests.factories import FeedFactory
from apps.feed.tests.factories import FeedItemFactory


class BaseViewSetTestMixin:
    def setUp(self) -> None:
        self.login_url: str = reverse('accounts-login')
        self.feed_item_user_url: str = reverse('feed-item-list')
        self.feed_url: str = reverse('feed-list')
        self.subscribe_url: str = reverse('feed-subscriber-list')


class ReaderViewSetTest(BaseViewSetTestMixin, APITestCase):

    def test_user_reader_feed(self) -> None:
        request: APIClient = self.client
        user = User.objects.create_user(
            username='string', password='testpass', email='misrax@misrax.com',
        )

        FeedItemFactory.create_batch(4)
        items = FeedItem.objects.all()
        readers = []
        for item in items:
            reader = Reader(item=item, user=user)
            readers.append(reader)
        Reader.objects.bulk_create(readers)
        # Login User Reader
        # Update user password
        response = request.post(
            self.login_url, {
                'username': user.username, 'password': 'testpass',
            },
        )
        token = response.json()['token']
        response = request.get(self.feed_item_user_url)
        self.assertEqual(response.status_code, 401)
        request.credentials(HTTP_AUTHORIZATION='Token ' + token)
        # Create another batch
        response = request.get(self.feed_item_user_url)
        self.assertEqual(response.json()['count'], 4)
        request.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = request.get(
            self.feed_item_user_url
            + '?read=1', )  # List all read items
        self.assertEqual(response.json()['count'], 4)
        response = request.get(
            self.feed_item_user_url
            + '?read=0', )  # List all read items
        self.assertEqual(response.json()['count'], 0)


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
        response = request.post(
            self.subscribe_url, data={
                'feeds': [feed[0].pk],
            },
        )
        self.assertEqual(response.status_code, 201)
        response = request.get(self.feed_url + '?subscribed=True')
        self.assertEqual(response.json()['count'], 1)
        response = request.get(self.feed_url + '?added_by_me=True')
        self.assertEqual(response.json()['count'], 1)
        response = request.get(self.feed_url + '?added_by_me=False')
        # Exclude added by the user
        self.assertEqual(response.json()['count'], 0)


class FeedViewSetTest(BaseViewSetTestMixin, APITestCase):

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend',
    )
    def test_create_feed(self) -> None:
        request: APIClient = self.client
        user: User = User.objects.create_user(
            username='misrax', password='hello', email='misrax@misrax.com',
        )
        response = request.post(
            self.login_url, {
                'username': user.username, 'password': 'hello',
            },
        )
        token = response.json()['token']
        request.credentials(HTTP_AUTHORIZATION='Token ' + token)

        response = request.post(
            self.feed_url, data={
                'name': 'front-end-feed-codrops',
                'url': 'http://www.nu.nl/rss/Algemeen',
            },
        )
        self.assertEqual(response.status_code, 201)
        feed_update_history = Feed.objects.get(
            **{
                'url': 'http://www.nu.nl/rss/Algemeen',
            },
        ).feed_update_history_latest()
        self.assertEqual(feed_update_history.status, DONE)
        self.assertTrue(FeedItem.objects.all())
        update_all_feeds.apply()
