from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import FeedUpdateHistory
from apps.feed.models import Reader
from apps.feed.models import Subscribe


class FeedUpdateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedUpdateHistory
        exclude = ('feed', 'updated_by', 'errors')
        read_only_fields = (
            'modified', 'created', 'status',
        )


class FeedSerializer(serializers.ModelSerializer):
    """
    Feed serializer
    """
    feed_update_history_latest = FeedUpdateHistorySerializer(
        allow_null=True, read_only=True,
    )

    class Meta:
        model = Feed
        exclude = ('user',)
        read_only_fields = (
            'modified',
            'created',
            'modified_method',
            'source_etag',
            'source_modified_at',
        )

    def create(self, validated_data):
        """
        Create a new feed with the request.user

        :param validated_data: dict
        :return: Feed
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class SubscribeSerializer(serializers.ModelSerializer):
    """
    User subscription serializer
    """

    class Meta:
        model = Subscribe
        fields = ('id', 'feeds')
        read_only_fields = ('created',)

    def create(self, validated_data):
        """
        Create a new subscription if it doesn't exist, otherwise return the existing one

        :param validated_data: dict
        :return: Subscription
        """
        user = self.context['request'].user
        try:
            subscription = Subscribe.objects.get(user=user)
        except Subscribe.DoesNotExist:
            validated_data['user'] = user
            return super().create(validated_data)
        return subscription

    def update(self, instance, validated_data) -> Subscribe:
        """
        Update an existing subscription

        :param instance: Subscription
        :param validated_data: dict
        :return: Subscribe
        """
        for feed in validated_data['feeds']:
            instance.feeds.add(feed)
        instance.save()
        return instance


class UnSubscribeSerializer(SubscribeSerializer):
    def update(self, instance: Subscribe, validated_data: dict) -> Subscribe:
        """
        Update an existing subscription

        :param instance: Subscription
        :param validated_data: dict
        :return: Subscription
        """
        for feed in validated_data['feeds']:
            instance.feeds.remove(feed)
        instance.save()
        return instance


class FeedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedItem
        fields = '__all__'


class ReadSerializer(serializers.ModelSerializer):
    """
    User reader serializer
    """
    item = FeedItemSerializer()

    class Meta:
        model = Reader
        fields = ['id', 'item']
        read_only_fields = ('created',)

    def validate_item(self, value):
        user = self.context['request'].user
        try:
            Reader.objects.get(item=value, user=user)
            raise serializers.ValidationError(_('Feed item already exists'))
        except Reader.DoesNotExist:
            return value

    def create(self, validated_data):
        """
        Create a new Read with the request.user

        :param validated_data: dict
        :return: Read
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
