from django.test.testcases import TestCase

from apps.feed.models import FeedItem
from apps.feed.parser import parse_feed
from apps.feed.tests.factories import FeedFactory


class ParserTest(TestCase):
    def test_parse_feed(self):
        feed: list = FeedFactory.create_batch(1)
        parsed, feed_items = parse_feed(feed[0])
        if parsed:
            self.assertEqual(
                FeedItem.objects.all().count(),
                feed_items.__len__(),
            )
