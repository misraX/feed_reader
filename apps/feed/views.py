from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet

from apps.feed.models import Feed
from apps.feed.models import Subscribe
from apps.feed.serializers import FeedSerializer
from apps.feed.serializers import SubscribeSerializer
from apps.feed.serializers import UnSubscribeSerializer


class FeedViewSet(ModelViewSet):
    serializer_class = FeedSerializer
    queryset = Feed.objects.all()


class SubscribeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    User Subscriber for any feed
    """
    serializer_class = SubscribeSerializer
    queryset = Subscribe.objects.all().prefetch_related('feeds')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)


class UnSubscribeViewSet(
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    User Subscriber for any feed
    """
    serializer_class = UnSubscribeSerializer
    queryset = Subscribe.objects.all().prefetch_related('feeds')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
