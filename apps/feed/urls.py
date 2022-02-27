from rest_framework.routers import DefaultRouter

from apps.feed.views import FeedViewSet
from apps.feed.views import SubscribeViewSet
from apps.feed.views import UnSubscribeViewSet
from apps.feed.views import UserFeedViewSet
router = DefaultRouter()
router.register(
    r'feed',
    FeedViewSet,
    basename='feed',
)
router.register(r'subscribe/feeds', UserFeedViewSet, basename='feed-user')
router.register(r'subscribe', SubscribeViewSet, basename='feed-subscriber')
router.register(
    r'unsubscribe', UnSubscribeViewSet,
    basename='feed-unsubscribe',
)
urlpatterns = router.urls
