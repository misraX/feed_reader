from django_filters import OrderingFilter
from django_filters import rest_framework as filters

from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader
from apps.feed.models import Subscribe


class FeedFilterSet(filters.FilterSet):
    subscribed = filters.BooleanFilter(method='filter_subscribed')
    order = OrderingFilter(
        fields=('modified', 'created'),

        field_labels={
            'modified': 'Feed updated at, last modified from the source',
            'created': 'List feed by created date',
        },
    )

    class Meta:
        model = Feed
        fields = ['user', 'name', 'url', 'modified']

    def filter_subscribed(self, queryset, name, value):
        """
        This filter should get all the followed feeds from the user's Subscribe model,
        All the Subscribe.objects.get(user=self.request.user).items.all() will be the feeds
        that had been followed, otherwise, return global feeds (queryset)
        """
        if value and value is not None and self.request:
            try:
                subscribe_queryset = Subscribe.objects.get(
                    user=self.request.user,
                )
                return queryset.filter(id__in=subscribe_queryset.feeds.all().values('id'))
            except Subscribe.DoesNotExist:
                return queryset.none()
        return queryset


class FeedItemFilterSet(filters.FilterSet):
    read = filters.BooleanFilter(method='filter_read')
    order = OrderingFilter(
        fields=('created',),

        field_labels={
            'created': 'List feed items by created date',
        },
    )

    class Meta:
        model = FeedItem
        fields = ['feed', 'read', 'order']

    def filter_read(self, queryset, name, value):
        """
        This filter should get all the read items from the user's Reader model,
        All the Reader.objects.get(user=self.request.user).items.all() will be the items
        that had been marked as read, otherwise, return global feed-items (queryset)
        """

        if value and value is not None and self.request:
            try:
                reader_queryset = Reader.objects.get(user=self.request.user)
                return queryset.filter(id__in=reader_queryset.items.all().values('id'))
            except Reader.DoesNotExist:
                return queryset.none()
        return queryset
