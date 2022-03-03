import logging
from datetime import datetime
from time import mktime
from typing import List
from typing import Tuple

import feedparser
import pytz
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from feedparser import FeedParserDict

from apps.feed.exceptions import FeedHasBeenDeletedException
from apps.feed.models import DONE
from apps.feed.models import ETAG
from apps.feed.models import FAILED
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import FeedUpdateHistory
from apps.feed.models import MODIFIED
from apps.feed.models import UPDATING

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


def parse(feed: Feed) -> Tuple[FeedParserDict, bool, Exception]:
    """
    MUST BE ATOMIC

    Parse a given feed and create feed_items

    :param feed: Feed
    :return: FeedParserDict
    """
    feed_url = feed.url
    if feed.modified_method == ETAG:
        parser = feedparser.parse(feed_url, etag=feed.source_etag)
    elif feed.modified_method == MODIFIED:
        parser = feedparser.parse(feed_url, modified=feed.source_modified_at)
    else:
        parser = feedparser.parse(feed_url)
    bozo = parser.get('bozo', False)
    bozo_exception = parser.get('bozo_exception', None)
    return parser, bozo, bozo_exception


def parse_feed(feed_id: int):
    """
    MUST BE ATOMIC

    :param feed_id: int
    :return: FeedParserDict
    """
    try:
        feed: Feed = Feed.objects.get(id=feed_id)
        last_updated = feed.feed_update_history_latest()
        logger.info(
            f'[FEED PARSER] Last updated FeedUpdateHistory for feed {feed.id} is {last_updated}',
        )
        if last_updated.status == DONE:
            logger.info(
                f'[FEED PARSER] Creating FeedUpdateHistory for feed {feed.id}',
            )
            last_updated: FeedUpdateHistory = FeedUpdateHistory.objects.create(
                feed=feed,
            )
        if last_updated.status not in [FAILED, UPDATING]:
            parser, bozo, bozo_exception = parse(feed)
            if bozo:
                msg = f'{bozo_exception}'
                last_updated.bozo = True  # Mark feed as bozo
                last_updated.errors = {
                    'error': msg,
                }
                last_updated.status = FAILED
                last_updated.save()
                logger.error(
                    f'[FEED PARSER] Updating FeedUpdateHistory for feed '
                    f'{feed.id} {feed.url} failed with {msg}',
                )
                raise bozo_exception
            last_updated.status = UPDATING
            last_updated.save()
            logger.info(
                f'[FEED PARSER] Updating FeedUpdateHistory for feed {feed.id} is {last_updated.status}',
            )
            return parser
    except Feed.DoesNotExist:
        msg = f'[FEED PARSER] Feed has been deleted/or does not exist'
        logger.error(msg)
        raise FeedHasBeenDeletedException(msg)


def parse_atomic(feed_id: int) -> None:
    """
    Atomic creation for parsing and creating feed items.
    The main usage of this function is inside a celery task, background tasks and periodic tasks

    Points:
    ---
    1. Passing the feed_id is better than the feed object and less costly on the message channel,
     plus if the feed deleted while the task is running
    2. IF THE FEED DOES NOT EXIST NO POINT FROM BREAKING

    :param feed_id: int
    :return: None
    """
    feed: QuerySet = Feed.objects.none()
    try:
        feed: Feed = Feed.objects.get(id=feed_id)
    except Feed.DoesNotExist:
        pass
    if feed:
        parsed_feed = parse_feed(feed.id)
        try:
            with transaction.atomic():
                modified, entries = entries_partial_modification(
                    parsed_feed, feed,
                )
                if modified:
                    create_feed_items(feed, entries, parsed_feed)
        except Exception as error:
            msg = str(error)
            update_history = feed.feed_update_history_latest()
            update_history.status = FAILED
            update_history.errors = msg
            update_history.save()
            logger.error(
                f'[FEED PARSER] Updating FeedUpdateHistory for feed '
                f'{feed.id} failed with {msg}',
            )


def get_partial_method(parsed_feed: FeedParserDict) -> str:
    """
    Get whether the partial GET is by ETAG or Last-Modified

    :param parsed_feed: FeedParserDict
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
    :return: int
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


def create_feed_items(feed: Feed, entries: List, parser: FeedParserDict) -> List:
    """
    MUST BE ATOMIC

    Bulk create feed items for a given feed and feed_entries

    :param parser: FeedParserDict
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
            language=parser.get('feed', {}).get('language', ''),
            item_id=entry.get('id', ''),
            copyright=entry.get('rights', ''),
            image=entry.get('image', {}),
        )
        feed_items.append(feed_item)
    FeedItem.objects.bulk_create(feed_items, batch_size=10)
    feed_history = feed.feed_update_history_latest()
    feed_history.status = DONE

    feed_history.save()
    logger.info(
        f'[FEED PARSER] Updating FeedUpdateHistory for feed {feed.id}'
        f' is {feed_history.status}',
    )
    return feed_items
