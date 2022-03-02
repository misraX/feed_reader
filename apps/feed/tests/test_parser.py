from urllib.error import URLError

from django.test.testcases import TestCase

from apps.feed.models import FAILED
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import FeedUpdateHistory
from apps.feed.parser import create_feed_items
from apps.feed.parser import entries_partial_modification
from apps.feed.parser import parse_feed
from apps.feed.tests.factories import FeedFactory


class ParserTest(TestCase):
    def test_parse_feed(self):
        feed: list[Feed] = FeedFactory.create_batch(1)
        parsed_feed = parse_feed(feed[0].id)
        modified, entries = entries_partial_modification(parsed_feed, feed[0])
        if modified:
            create_feed_items(feed[0], entries, parsed_feed)
        self.assertEqual(
            entries.__len__(),
            FeedItem.objects.filter(feed=feed[0]).count(),
        )

    def test_parse_feed_failure(self):
        feed: Feed = Feed.objects.create(
            **{
                'name': 'tweakers',
                'url': 'https://feeds.feedburner1.com/tweakers/mixed',
            },
        )
        self.assertRaises(URLError, parse_feed, feed.id)
        feed_update_history = FeedUpdateHistory.objects.all()
        self.assertEqual(feed_update_history.count(), 1)
        feed = Feed.objects.get(
            **{'url': 'https://feeds.feedburner1.com/tweakers/mixed'},
        )
        feed_latest_update_history = feed.feed_update_history_latest
        self.assertEqual(feed_latest_update_history().status, FAILED)
