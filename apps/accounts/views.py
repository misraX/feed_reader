from django.contrib.auth import get_user_model
from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from apps.accounts.serializers import UserSerializer


class RegisterView(CreateAPIView):
    """
    Register users
    """
    model = get_user_model()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class LoginView(GenericAPIView, KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AuthTokenSerializer

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super().post(request, format=None)
