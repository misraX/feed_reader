from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class User(TimeStampedModel, AbstractUser):
    email = models.EmailField(_('email address'), blank=True, unique=True)

    class Meta:
        ordering = ['-created']
        unique_together = ['username', 'email']
