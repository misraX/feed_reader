from django.db import transaction

from apps.feed.models import Feed
from apps.feed.parser import create_feed_items
from apps.feed.parser import entries_partial_modification
from apps.feed.parser import parse_feed
from feed_reader.celery import app


@app.task(
    name='update_feed',
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5},
)
def update_feed(task, feed_id: int):
    feed: Feed = Feed.objects.get(feed_id=feed_id)
    parsed_feed = parse_feed(feed.id)

    with transaction.atomic():
        modified, entries = entries_partial_modification(parsed_feed, feed)
        if modified:
            create_feed_items(feed, entries, parsed_feed)
