import logging
from datetime import datetime
from time import mktime
from typing import List
from typing import Tuple

import feedparser
import pytz
from django.conf import settings
from feedparser import FeedParserDict

from apps.feed.models import ETAG
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import MODIFIED

logger = logging.getLogger('feed_parser')


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
            pub_date=datetime.fromtimestamp(
                mktime(entry.get('published_parsed')),
                tz=pytz.timezone(settings.TIME_ZONE),
            ),
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


def check_for_modification(feed: Feed, partial_method: str, parser: FeedParserDict) -> None:
    """
    Check for modification from the source
    :param feed: Feed
    :param partial_method: str
    :param parser: FeedParserDict
    :return: None
    """
    if feed.modified_method != partial_method:
        feed.modified_method = partial_method
    if partial_method == ETAG:
        if feed.source_etag != parser.etag:
            feed.source_etag = parser.etag
    else:
        if feed.source_modified_at != parser.modified:
            feed.source_modified_at = parser.modified
    feed.save()


def parse_feed(feed: Feed) -> Tuple[bool, List] | Tuple[bool, List]:
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
    check_for_modification(feed, partial_method, parser)
    if parser.entries:
        feed_items = create_feed_item(feed, parser.entries)
        logger.info(f'[FEED PARSER] Feed {feed} updated')
        return True, feed_items
    logger.info(f'[FEED PARSER] Feed {feed} is already up to date')
    return False, []
