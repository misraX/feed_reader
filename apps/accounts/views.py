from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.accounts.serializers import UserSerializer


class RegisterView(CreateAPIView):
    """
    Register users
    """
    model = get_user_model()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
