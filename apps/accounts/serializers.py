from __future__ import annotations

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    User model serializer.
    Auto generating username if username not found.
    """

    def validate_username(self, value: str) -> str:
        """
        Validate registration username.

        :param value:
        :return:
        """
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            return value
        raise serializers.ValidationError(_('Username already exist.'))

    def create(self, validated_data: dict) -> User:
        """
        Create a new user.
        :param validated_data:
        :return:
        """
        user = User.objects.create(
            **validated_data,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
