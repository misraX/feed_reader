from email.utils import parsedate_to_datetime

import feedparser
from feedparser import FeedParserDict

from apps.feed.models import ETAG
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import MODIFIED


def partial_get_method(parsed_feed: FeedParserDict) -> str:
    """
    Get whether the partial GET is by ETAG or Last-Modified
    :return: str
    """
    method = ETAG
    try:
        parsed_feed.etag
    except AttributeError:
        try:
            parsed_feed.modified
            method = MODIFIED
        except AttributeError:
            pass
    return method


def create_feed_item(feed: Feed, entries: list) -> list:
    """
    Bulk create feed items for a given feed and feed_entries

    :param feed: Feed
    :param entries: []
    :return: None
    """
    feed_items = []
    for entry in entries:
        feed_item: FeedItem = FeedItem(
            feed=feed,
            pub_date=str(parsedate_to_datetime(entry.get('published'))),
            title=entry.get('title'),
            link=entry.get('link'),
            description=entry.get('description'),
            language=entry.get('language', ''),
            item_id=entry.get('id', ''),
            copyright=entry.get('copyright', ''),
            image=entry.get('image', {}),
        )
        feed_items.append(feed_item)
    FeedItem.objects.bulk_create(feed_items, batch_size=10)
    return feed_items


def parse_feed(feed: Feed) -> tuple[bool, list] | tuple[bool, list]:
    """
    Parse a given feed and create feed_items

    :param feed: Feed
    :return: tuple[bool, list] | tuple[bool, list]
    """
    feed_url = feed.url
    if feed.modified_method == ETAG:
        parser = feedparser.parse(feed_url, etag=feed.source_etag)
    elif feed.modified_method == MODIFIED:
        parser = feedparser.parse(feed_url, modified=feed.source_modified_at)
    else:
        parser = feedparser.parse(feed_url)
        partial_method = partial_get_method(parser)
        feed.modified_method = partial_method
        feed.save()
    if parser.entries:
        feed_items = create_feed_item(feed, parser.entries)
        return True, feed_items
    return False, []
