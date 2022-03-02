from apps.feed.parser import parse_atomic
from feed_reader.celery import app


@app.task(
    name='update_feed',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def update_feed(feed_id: int):
    """
    Update a give feed based on the feed.id
    :param feed_id: int
    :return: bool
    """
    parse_atomic(feed_id)
    return True
