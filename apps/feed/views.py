from django.db import transaction
from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet

from apps.feed.filters import FeedFilterSet
from apps.feed.filters import FeedItemFilterSet
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader
from apps.feed.models import Subscribe
from apps.feed.permission import ObjectOwnerAccessPermission
from apps.feed.serializers import FeedItemSerializer
from apps.feed.serializers import FeedSerializer
from apps.feed.serializers import ReadSerializer
from apps.feed.serializers import SubscribeSerializer
from apps.feed.serializers import UnSubscribeSerializer
from apps.feed.tasks import update_feed


class OwnerPermissionViewMixin:
    """
    Force ownership of the model instance, to the requested user

    Two layers:
    1. Permission based, through 403
    2. Model based, filter the db for the object owner
    """
    permission_classes = (IsAuthenticated, ObjectOwnerAccessPermission)
    INSTANCE = None

    def get_queryset(self) -> QuerySet:
        """
        Force the view to get only the request.user subscription

        :return: Queryset
        """
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return self.INSTANCE.objects.none()


class FeedViewSet(ModelViewSet):
    """
    List all feeds with filters ['name', 'url', 'modified', 'subscribed', 'added_by_me' ,'order']

    'name': filter all feeds by a give name
    'modified': filter all feeds by modified date
    'subscribed': filter all feeds by the subscribed feeds
    'added_by_me': filter all feeds by the request.user
    'order': order feeds by created, modified
    """
    serializer_class = FeedSerializer
    filterset_class = FeedFilterSet
    queryset = Feed.objects.all()

    @transaction.atomic
    def perform_create(self, serializer: FeedSerializer):
        super().perform_create(serializer)
        update_feed.apply_async((serializer.data.get('id'),))


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


class SubscriptionMixin:
    """
    Common Subscription view's mixin for subscription and un-subscription
    """
    serializer_class = SubscribeSerializer
    queryset = Subscribe.objects.all().prefetch_related('feeds')


class SubscribeViewSet(
    SubscriptionMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    User Subscriber for one or many feed
    """
    pass


class UnSubscribeViewSet(
    SubscriptionMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    User Un-Subscriber for one or many feeds
    """
    serializer_class = UnSubscribeSerializer


class ReaderViewMixin:
    """
    Common user's Reader view mixin
    """
    serializer_class = ReadSerializer
    queryset = Reader.objects.all()
    INSTANCE = Reader


class ReaderViewSet(
    OwnerPermissionViewMixin,
    ReaderViewMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    Read one or many feed items
    """
    pass


class UnReadViewSet(
    OwnerPermissionViewMixin,
    ReaderViewMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    Unread one or many feed items
    """
    pass


class ForceUpdateFeedViewSet(OwnerPermissionViewMixin, mixins.RetrieveModelMixin, GenericViewSet):
    """
    Force update feed
    """
    serializer_class = FeedSerializer
    queryset = Feed.objects.all()

    def retrieve(self, request, pk, *args, **kwargs):
        """
        Force update feed

        The owner of the feed can force updating the feed in an async way.
        The celery task and model signal will update and notify the user if their is a failure occurred
        """
        update_feed.apply_async((pk,))
        return super().retrieve(request, pk, *args, **kwargs)
