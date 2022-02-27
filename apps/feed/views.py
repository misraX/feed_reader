from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet

from apps.feed.filters import FeedFilterSet
from apps.feed.filters import FeedItemFilterSet
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader
from apps.feed.models import Subscribe
from apps.feed.serializers import FeedItemSerializer
from apps.feed.serializers import FeedSerializer
from apps.feed.serializers import ReaderSerializer
from apps.feed.serializers import SubscribeSerializer
from apps.feed.serializers import UnReadSerializer
from apps.feed.serializers import UnSubscribeSerializer


class FeedViewSet(ModelViewSet):
    """
    List all feeds with filters ['user', 'name', 'url', 'last_modified', 'subscribed', 'order']
    'user': filter all feeds registered by a given user
    'name': filter all feeds by a give name
    'last_modified': filter all feeds by last_modified date
    'subscribed': filter all the followed feeds by the user's Subscribe model
    'order': order feeds by created, last_modified
    """
    serializer_class = FeedSerializer
    filterset_class = FeedFilterSet
    queryset = Feed.objects.all()


class SubscriptionMixin:
    """
    Common Subscription view's mixin for subscription and un-subscription
    """
    serializer_class = SubscribeSerializer
    queryset = Subscribe.objects.all().prefetch_related('feeds')

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return Subscribe.objects.none()


class SubscribeViewSet(
    SubscriptionMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    User Subscriber for any feed
    """
    pass


class UnSubscribeViewSet(
    SubscriptionMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    User Subscriber for any feed
    """
    serializer_class = UnSubscribeSerializer


class FeedItemViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all feed items with filters ['feed', 'read', 'order']
    'read': filter all feed items by items that has been included in the Reader profile
    'feed': filter all feed items by a give feed
    'order': order feed items by created, (creation date)
    """
    serializer_class = FeedItemSerializer
    queryset = FeedItem.objects.all()
    filterset_class = FeedItemFilterSet


class ReaderMixin:
    """
    Common Reader view's mixin for read and unread feed items
    """
    serializer_class = ReaderSerializer
    queryset = Reader.objects.all().prefetch_related('items')

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return Subscribe.objects.none()


class ReadViewSet(
    ReaderMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    Read one or many feed items
    """
    pass


class UnReadViewSet(
    ReaderMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    Unread one or many feed items
    """
    serializer_class = UnReadSerializer
