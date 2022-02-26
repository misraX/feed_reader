from rest_framework.routers import DefaultRouter

from apps.feed.views import FeedViewSet
from apps.feed.views import SubscribeViewSet

router = DefaultRouter()
router.register(r'feed', FeedViewSet, basename='feed')
router.register(r'subscribe', SubscribeViewSet, basename='feed-subscriber')
urlpatterns = router.urls
