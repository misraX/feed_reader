from django.db.models import QuerySet
from django_filters import OrderingFilter
from django_filters import rest_framework as filters

from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader
from apps.feed.models import Subscribe


class FeedFilterSet(filters.FilterSet):
    subscribed = filters.BooleanFilter(method='filter_subscribed')
    added_by_me = filters.BooleanFilter(method='filter_added_by_me')
    order = OrderingFilter(
        fields=('modified', 'created'),

        field_labels={
            'modified': 'Feed updated at, last modified from the source',
            'created': 'List feed by created date',
        },
    )

    class Meta:
        model = Feed
        fields = ['name', 'url', 'modified']

    def filter_subscribed(self, queryset: QuerySet, name, value):
        """
        This filter should get all the followed feeds from the user's Subscribe model,
        All the Subscribe.objects.get(user=self.request.user).items.all() will be the feeds
        that had been followed, otherwise, return global feeds (queryset)
        """
        if value and value is not None:
            try:
                user_subscription_queryset = Subscribe.objects.get(
                    user=self.request.user,
                )
                subscribed_queryset = queryset.filter(
                    id__in=user_subscription_queryset.feeds.all().values('id'),
                )
                return subscribed_queryset
            except Subscribe.DoesNotExist:
                return queryset.none()
        return queryset

    def filter_added_by_me(self, queryset: QuerySet, name, value):
        """
        Get all request.user related feeds, the related feeds are the feeds
        added by the request.user.

        :param queryset: Queryset
        :param name: str
        :param value: str
        :return: Queryset
        """
        added_by_me_queryset = Feed.objects.filter(user=self.request.user)
        if value and value is not None:
            return added_by_me_queryset
        return queryset.exclude(user=self.request.user)


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

    def filter_read(self, queryset: QuerySet, name, value):
        """
        This filter should get all the read items from the user's Reader model,
        All the Reader.objects.get(user=self.request.user).items.all() will be the items
        that had been marked as read, otherwise, return global feed-items (queryset)
        """
        reader_queryset = Reader.objects.filter(user=self.request.user)
        if value and value is not None:
            return queryset.filter(id__in=reader_queryset.values('item_id'))
        return queryset.exclude(id__in=reader_queryset.values('item_id'))
