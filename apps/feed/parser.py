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


def check_for_modification(feed: Feed, partial_method: str, parser: FeedParserDict) -> None:
    """
    Check for modification from the source, whether it's ETAG or Last-Modified

    The function check for the existence of the partial method method for a given feed
    1. Detect if the feed has the same partial method
    2. Update the feed with modification value of the ETAG/or Last-Modified

    :param feed: Feed
    :param partial_method: str
    :param parser: FeedParserDict
    :return: None
    """
    if feed.modified_method != partial_method:
        feed.modified_method = partial_method
    if partial_method == ETAG:  # ETAG DETECTED
        if feed.source_etag != parser.etag:  # ETAG ISN'T THE SAME
            feed.source_etag = parser.etag
            feed.save()
    else:  # IS-MODIFIED DETECTED
        if feed.source_modified_at != parser.modified:  # IS-MODIFIED ISN'T THE SAME
            feed.source_modified_at = parser.modified
            feed.save()


def parse_feed(feed: Feed) -> FeedParserDict:
    """
    Parse a given feed and create feed_items

    :param feed: Feed
    :return: tuple[bool, List]
    """
    feed_url = feed.url
    if feed.modified_method == ETAG:
        parser = feedparser.parse(feed_url, etag=feed.source_etag)
    elif feed.modified_method == MODIFIED:
        parser = feedparser.parse(feed_url, modified=feed.source_modified_at)
    else:
        parser = feedparser.parse(feed_url)
    return parser


def get_partial_method(parsed_feed: FeedParserDict) -> str:
    """
    Get whether the partial GET is by ETAG or Last-Modified

    :param parsed_feed:
    :return: str
    """
    method = ETAG
    try:
        parsed_feed.etag
    except AttributeError:
        pass
    try:
        parsed_feed.modified
        method = MODIFIED
    except AttributeError:
        pass
    return method


def check_for_bozo(parser: FeedParserDict) -> int:
    """
    Check for not-well formed feeds
    :param parser: FeedParserDict
    :return: 0|1
    """
    return parser['bozo']


def entries_partial_modification(parser: FeedParserDict, feed: Feed) -> Tuple[bool, List]:
    """
    After parsing the feed, check if the feed is entitled for update or not, the partial modification
    will check the entries and return the updated entries along with True, or an emtpy list with False

    :param parser: FeedParserDict
    :param feed: Feed
    :return: Tuple[bool, List]
    """
    partial_method = get_partial_method(parser)
    check_for_modification(feed, partial_method, parser)
    entries = parser.entries
    if entries:
        logger.info(
            f'[FEED PARSER] Feed {feed} contains an update, create_feed_items is required to update the DB',
        )
        return True, entries
    logger.info(f'[FEED PARSER] Feed {feed} is already up to date 😀')
    return False, entries


def create_feed_items(feed: Feed, entries: List) -> List:
    """
    Bulk create feed items for a given feed and feed_entries

    :param feed: Feed
    :param entries: List
    :return: List
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
