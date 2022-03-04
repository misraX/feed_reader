import time
from contextlib import contextmanager
from hashlib import md5

from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.db.models import QuerySet

from apps.feed.models import Feed
from apps.feed.parser import parse_atomic
from feed_reader.celery import app

logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 2  # Lock expires in 10 minutes 🤩


@contextmanager
def memcached_lock(lock_id, oid):
    """
    Inspired by: https://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html#ensuring-a-task-is-only-executed-one-at-a-time

    :param lock_id: md5
    :param oid: uuid
    :return: None
    """
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


def check_for_lock(self, feed_id: int):
    """
    Inspired by: https://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html#ensuring-a-task-is-only-executed-one-at-a-time

    :param self: AsyncTask
    :param feed_id: int
    :return:
    """
    feed_id_hexdigest = md5(str(feed_id).encode('utf-8')).hexdigest()
    lock_id = f'{self.name}-lock-{feed_id_hexdigest}'
    logger.info(f'Importing feed: {feed_id}')
    with memcached_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            logger.info(f'Task is acquired, Importing feed: {feed_id}')
            return parse_atomic(feed_id)
    logger.info(f'Feed {feed_id} is already being imported by another worker')


@app.task(
    name='update_feed',
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def update_feed(self, feed_id: int):
    """

    :param self: AsyncTask
    :param feed_id: int
    :return:
    """
    return check_for_lock(self, feed_id)


@app.task(
    name='update_all_feeds',
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def update_all_feeds(self):
    """
    Update all feeds, preferred to be used in a crontab like approach

    :param self: AsyncTask
    :return: None
    """
    logger.info(f'Feeds update started')
    feeds: QuerySet = Feed.objects.all()
    if feeds:
        for feed in feeds:
            feed_id = feed.id
            logger.info(f'Feed update started: {feed_id}')
            update_feed.apply_async((feed_id,))
    logger.info('Feeds have been updated')
    return True
