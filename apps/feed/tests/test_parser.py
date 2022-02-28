from django.test.testcases import TestCase

from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.parser import create_feed_items
from apps.feed.parser import entries_partial_modification
from apps.feed.parser import parse_feed
from apps.feed.tests.factories import FeedFactory


class ParserTest(TestCase):
    def test_parse_feed(self):
        feed: list[Feed] = FeedFactory.create_batch(1)
        parsed_feed = parse_feed(feed[0])
        modified, entries = entries_partial_modification(parsed_feed, feed[0])
        if modified:
            create_feed_items(feed[0], entries)
        self.assertEqual(
            entries.__len__(),
            FeedItem.objects.filter(feed=feed[0]).count(),
        )
