from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.feed.models import Feed
from apps.feed.models import FeedItem
from apps.feed.models import Reader
from apps.feed.models import Subscribe


class FeedSerializer(serializers.ModelSerializer):
    """
    Feed serializer
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Feed
        fields = '__all__'
        read_only_fields = ('modified', 'created', 'user')

    def create(self, validated_data):
        """
        Create a new subscription if it doesn't exist, otherwise return the existing one

        :param validated_data: dict
        :return: Subscription
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class SubscribeSerializer(serializers.ModelSerializer):
    """
    User subscription serializer
    """
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
    feed = FeedSerializer(read_only=True)

    class Meta:
        model = FeedItem
        fields = '__all__'


class ReaderSerializer(serializers.ModelSerializer):
    """
    User reader serializer
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reader
        fields = ('id', 'items', 'user')
        read_only_fields = ('created',)

    def create(self, validated_data: dict):
        """
        Create a new reader if it doesn't exist, otherwise return the existing one

        :param validated_data: dict
        :return: Reader
        """
        user = self.context['request'].user
        try:
            reader = Reader.objects.get(user=user)
        except Reader.DoesNotExist:
            validated_data['user'] = user
            return super().create(validated_data)
        return reader

    def update(self, instance: Reader, validated_data) -> Reader:
        """
        Update an existing reader, from the given items

        :param instance: Reader
        :param validated_data: dict
        :return: Reader
        """
        for item in validated_data['items']:
            instance.items.add(item)
        instance.save()
        return instance


class UnReadSerializer(ReaderSerializer):
    def update(self, instance: Reader, validated_data: dict) -> Reader:
        """
        Update an existing reader

        :param instance: Reader
        :param validated_data: dict
        :return: Subscription
        """
        for item in validated_data['items']:
            instance.items.remove(item)
        instance.save()
        return instance
