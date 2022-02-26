from rest_framework import serializers

from apps.feed.models import Feed
from apps.feed.models import UserFeed


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('name', 'url', 'last_modified', 'created')


class UserFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeed
        fields = ('user', 'feed', 'created')
