from apps.feed.models import Feed
from apps.feed.parser import create_feed_items
from apps.feed.parser import entries_partial_modification
from apps.feed.parser import parse_feed
from apps.feed.tests.factories import FeedFactory
from feed_reader.celery import app


@app.task(bind=True)
def debug_task(args):
    FeedFactory.create_batch(8)
    feeds = Feed.objects.all()
    for feed in feeds:
        parsed_feed = parse_feed(feed)
        modified, entries = entries_partial_modification(parsed_feed, feed)
        if modified:
            create_feed_items(feed, entries)
    return True
