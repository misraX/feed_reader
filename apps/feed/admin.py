from django.contrib import admin

from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import FeedUpdateHistory
from apps.feed.models import Reader
from apps.feed.models import Subscribe

admin.site.register(FeedItem)
admin.site.register(Feed)
admin.site.register(FeedUpdateHistory)

admin.site.register(Reader)
admin.site.register(Subscribe)
