from rest_framework.routers import DefaultRouter

from apps.feed.views import FeedItemViewSet
from apps.feed.views import FeedViewSet
from apps.feed.views import ReaderViewSet
from apps.feed.views import SubscribeViewSet
from apps.feed.views import UnReadViewSet
from apps.feed.views import UnSubscribeViewSet

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
router.register(r'read', ReaderViewSet, basename='feed-item-read')
router.register(
    r'unread', UnReadViewSet,
    basename='feed-item-unread',
)

urlpatterns = router.urls
