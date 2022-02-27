from django_filters import OrderingFilter
from django_filters import rest_framework as filters

from apps.feed.models import Feed
from apps.feed.models import FeedItem


class FeedFilterSet(filters.FilterSet):
    order = OrderingFilter(
        fields=('last_modified',),

        field_labels={
            'last_modified': 'Feed updated at, last modified from the source',
        },
    )

    class Meta:
        model = Feed
        fields = ['name', 'url', 'last_modified']


class FeedItemFilterSet(filters.FilterSet):
    class Meta:
        model = FeedItem
        fields = ['feed']
