from email.utils import parsedate_to_datetime

from rest_framework.test import APITestCase

from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Subscribe


class SubscribeViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.feed_model = Feed
        self.feed_item_model = FeedItem
        self.user_feed_model = Subscribe
        self.feed_data: dict = {
            'name': 'washingtonpost',
            'url': 'http://feeds.washingtonpost.com/rss/world',
        }
        self.feed_item_data: dict = {
            'language': 'en-us',
            'copyright': 'Copyright 2002, Spartanburg Herald-Journal',
            'pub_date': str(parsedate_to_datetime('Sat, 07 Sep 2002 0:00:01 GMT')),
            'title': 'GoUpstate.com News Headlines',
            'link': 'http://www.goupstate.com/',
            'description': 'The latest news from GoUpstate.com, a Spartanburg Herald-Journal Web site.',
        }
