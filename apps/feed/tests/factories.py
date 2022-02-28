import factory
from django.utils import timezone

from apps.accounts.factories import UserFactory
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader
from apps.feed.models import Subscribe

FEED_LIST = [
    {'name': 'front-end-feed-codrops', 'url': 'https://tympanus.net/codrops/feed/'},
    {'name': 'front-end-feed-css-tricks', 'url': 'https://css-tricks.com/feed/'},
    {'name': 'front-end-feed-dev.to', 'url': 'https://dev.to/feed'},
    {'name': 'front-end-feed-tutsplus', 'url': 'https://code.tutsplus.com/posts.atom'},
    {'name': 'front-end-feed-hnrss', 'url': 'https://hnrss.org/frontpage'},
    {'name': 'front-end-feed-hackernoon', 'url': 'https://hackernoon.com/feed'},
    {'name': 'front-end-feed-sitepoint', 'url': 'https://www.sitepoint.com/feed/'},
    {
        'name': 'front-end-feed-smashingmagazine',
        'url': 'https://www.smashingmagazine.com/feed',
    },
    {
        'name': 'Algemeen',
        'url': 'http://www.nu.nl/rss/Algemeen',
    },
    {
        'name': 'tweakers',
        'url': 'https://feeds.feedburner.com/tweakers/mixed',
    },
]


class FeedFactory(factory.django.DjangoModelFactory):
    """
    A factory for the Feed
    """

    class Meta:
        model = Feed
        django_get_or_create = ('url',)

    name = factory.Iterator([feed['name'] for feed in FEED_LIST])
    url = factory.Iterator([feed['url'] for feed in FEED_LIST])
    user = factory.SubFactory(UserFactory)


def image_sequence(value: int) -> dict:
    return {
        'href': f'https://s3{value}.com',
        'link': f'https://s3{value}.com',
        'width': f'{value}',
        'height': f'{value}',
    }


class FeedItemFactory(factory.django.DjangoModelFactory):
    """
    A factory for Feed item
    """

    class Meta:
        model = FeedItem

    feed = factory.SubFactory(FeedFactory)
    title = factory.Iterator([
        'Volt zet Gündogan uit Kamerfractie na dertien meldingen over ongewenst gedrag',
        'Volt schorst Kamerlid Gündogan wegens meldingen grensoverschrijdend gedrag',
        'De coronacijfers van vandaag',
    ])
    link = factory.Faker('url')
    description = factory.Faker('text')
    language = factory.Iterator(['fr', 'it', 'es'])
    pub_date = factory.Faker(
        'date_time', tzinfo=timezone.get_current_timezone(),
    )
    item_id = factory.Sequence(lambda n: n)
    copyright = factory.Faker('name')
    image = factory.Sequence(image_sequence)


class SubscribeFactory(factory.django.DjangoModelFactory):
    """
    A factory for subscribe
    """

    class Meta:
        model = Subscribe

    user = factory.SubFactory(UserFactory)


class ReaderFactory(factory.django.DjangoModelFactory):
    """
    A factory for subscribe
    """

    class Meta:
        model = Reader

    user = factory.SubFactory(UserFactory)
