from django.urls import path
from knox.views import LogoutAllView
from knox.views import LogoutView

from apps.accounts.views import LoginView
from apps.accounts.views import RegisterView

urlpatterns = [
    path('register', RegisterView.as_view(), name='accounts-register'),
    path('login', LoginView.as_view(), name='accounts-login'),
    path('logout', LogoutView.as_view(), name='accounts-logout'),
    path('logout-all', LogoutAllView.as_view(), name='accounts-logout_all'),
]
