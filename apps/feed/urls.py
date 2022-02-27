from rest_framework.routers import DefaultRouter

from apps.feed.views import FeedItemViewSet
from apps.feed.views import FeedViewSet
from apps.feed.views import ReadViewSet
from apps.feed.views import SubscribeViewSet
from apps.feed.views import UnReadViewSet
from apps.feed.views import UnSubscribeViewSet
from apps.feed.views import UserFeedItemViewSet
from apps.feed.views import UserFeedViewSet

router = DefaultRouter()
router.register(
    r'feed',
    FeedViewSet,
    basename='feed',
)
router.register(
    r'feed-item',
    FeedItemViewSet,
    basename='feed-item',
)

router.register(r'subscribe', SubscribeViewSet, basename='feed-subscriber')
router.register(
    r'unsubscribe', UnSubscribeViewSet,
    basename='feed-unsubscribe',
)
router.register(r'read', ReadViewSet, basename='feed-subscriber')
router.register(
    r'unread', UnReadViewSet,
    basename='feed-unsubscribe',
)

router.register(r'user/feeds', UserFeedViewSet, basename='feed-user')
router.register(
    r'user/feed-items', UserFeedItemViewSet,
    basename='feed-item-user',
)
urlpatterns = router.urls
