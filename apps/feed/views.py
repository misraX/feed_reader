from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet

from apps.feed.serializers import FeedSerializer
from apps.feed.serializers import UserFeedSerializer


class FeedViewSet(ModelViewSet):
    serializer_class = FeedSerializer


class SubscribeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    User Subscriber for any feed
    """
    serializer_class = UserFeedSerializer
