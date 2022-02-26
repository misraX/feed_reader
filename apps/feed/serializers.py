from rest_framework import serializers

from apps.feed.models import Feed
from apps.feed.models import Subscribe


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('name', 'url', 'last_modified', 'created')


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'feed', 'created')
