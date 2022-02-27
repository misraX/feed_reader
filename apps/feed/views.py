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


class UserFeedViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = FeedSerializer
    filterset_class = FeedFilterSet
    queryset = Subscribe.objects.all().prefetch_related('feeds')

    def get_queryset(self) -> QuerySet:
        """
        Filter subscription based on the request.user, and then list all the related feeds
        :return:
        """
        if self.request.user.is_authenticated:
            try:
                queryset = self.queryset.get(user=self.request.user)
                feeds_queryset = queryset.feeds.all()
                return feeds_queryset
            except Subscribe.DoesNotExist:
                return Feed.objects.none()


class FeedItemViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = FeedItemSerializer
    queryset = FeedItem.objects.all()
    filterset_class = FeedItemFilterSet


class ReaderMixin:
    """
    Common Reader view's mixin for read and un-read
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
    User Subscriber for any feed
    """
    pass


class UnReadViewSet(
    ReaderMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    User Subscriber for any feed
    """
    serializer_class = UnReadSerializer


class UserFeedItemViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = FeedItemSerializer
    queryset = Reader.objects.all()
    filterset_class = FeedItemFilterSet

    def get_queryset(self) -> QuerySet:
        """
        Filter feed items based on the request.user, and then list all the related feed items
        :return: QuerySet
        """
        if self.request.user.is_authenticated:
            try:
                queryset = self.queryset.get(user=self.request.user)
                feeds_items_queryset = queryset.items.all()
                return feeds_items_queryset
            except Reader.DoesNotExist:
                return FeedItem.objects.none()
