from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet

from apps.feed.models import Feed
from apps.feed.models import Subscribe
from apps.feed.serializers import FeedSerializer
from apps.feed.serializers import SubscribeSerializer
from apps.feed.serializers import UnSubscribeSerializer
from apps.feed.serializers import UserFeedSerializer


class FeedViewSet(ModelViewSet):
    serializer_class = FeedSerializer
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
    serializer_class = UserFeedSerializer
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
                return Subscribe.objects.none()
