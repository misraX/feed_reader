from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.feed.models import Feed
from apps.feed.models import Subscribe


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('id', 'name', 'url', 'created')
        read_only_fields = ('last_modified', 'created')


class SubscribeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Subscribe
        fields = ('id', 'feeds', 'user')
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

    def update(self, instance, validated_data):
        """
        Update an existing subscription

        :param instance: Subscription
        :param validated_data: dict
        :return: Subscription
        """
        for feed in validated_data['feeds']:
            instance.feeds.add(feed)
        instance.save()
        return instance


class UnSubscribeSerializer(SubscribeSerializer):
    def update(self, instance: Subscribe, validated_data):
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
