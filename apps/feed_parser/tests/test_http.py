from django.test.testcases import TestCase

from apps.feed.models import FeedItem
from apps.feed.tests.factories import FeedFactory
from apps.feed_parser.http import parse_feed


class HTTPTestCase(TestCase):
    def test_parse_feed(self):
        feed: list = FeedFactory.create_batch(1)
        parsed, feed_items = parse_feed(feed[0])
        if parsed:
            self.assertEqual(
                FeedItem.objects.all().count(),
                feed_items.__len__(),
            )
