from django.contrib import admin

from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader

admin.site.register(FeedItem)
admin.site.register(Feed)
admin.site.register(Reader)
