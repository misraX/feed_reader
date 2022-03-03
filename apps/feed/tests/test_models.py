from email.utils import parsedate_to_datetime

from django.test import TestCase

from apps.accounts.models import User
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader
from apps.feed.models import Subscribe
from apps.feed.tests.factories import FEED_LIST
from apps.feed.tests.factories import FeedItemFactory


class ModelTestCase(TestCase):
    def setUp(self) -> None:
        self.feed_model = Feed
        self.feed_item_model = FeedItem
        self.user_feed_model = Subscribe
        self.feed_data: dict = {
            'name': 'washingtonpost',
            'url': 'http://feeds.washingtonpost.com/rss/world',
        }
        self.feed_item_data: dict = {
            'language': 'en-us',
            'copyright': 'Copyright 2002, Spartanburg Herald-Journal',
            'pub_date': str(parsedate_to_datetime('Sat, 07 Sep 2002 0:00:01 GMT')),
            'title': 'GoUpstate.com News Headlines',
            'link': 'http://www.goupstate.com/',
            'description': 'The latest news from GoUpstate.com, a Spartanburg Herald-Journal Web site.',
        }

    def test_created_feed(self) -> None:
        self.feed_model.objects.create(**self.feed_data)
        self.assertEqual(1, self.feed_model.objects.count())
        washingtonpost_feed = self.feed_model.objects.get(
            name=self.feed_data['name'],
        )
        self.assertEqual(washingtonpost_feed.name, self.feed_data['name'])
        self.assertEqual(washingtonpost_feed.url, self.feed_data['url'])

    def test_created_feed_item(self) -> None:
        feed = self.feed_model.objects.create(**self.feed_data)
        self.feed_item_data['feed'] = feed
        feed_item = self.feed_item_model.objects.create(
            **self.feed_item_data,
        )
        self.assertEqual(feed_item.title, self.feed_item_data['title'])
        self.assertEqual(feed_item.feed, feed)

    def test_user_feed(self) -> None:
        feed = self.feed_model.objects.create(**self.feed_data)
        user = User.objects.create_user(
            username='string', password='testpass', email='misrax@misrax.com',
        )

        user_feed = self.user_feed_model.objects.create(user=user)
        user_feed.feeds.add(feed)
        self.assertEqual(user_feed.user, user)
        self.assertEqual(user_feed.feeds.get(id=feed.id), feed)

    def test_user_reader_feed(self) -> None:
        feed_items = FeedItemFactory.create_batch(2)
        user = User.objects.create_user(
            username='string', password='testpass', email='misrax@misrax.com',
        )

        self.assertTrue(
            feed_items[0].feed.name in [
                feed['name'] for feed in FEED_LIST
            ],
        )
        # Add items to reader
        readers = []
        for item in feed_items:
            reader = Reader(item=item, user=user)
            readers.append(reader)
        Reader.objects.bulk_create(readers)
        reader: Reader = Reader.objects.filter(user=user).count()
        self.assertEqual(reader, feed_items.__len__())
