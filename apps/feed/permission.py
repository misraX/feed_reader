from django.utils.translation import gettext_lazy as _
from rest_framework import permissions


class ObjectOwnerAccessPermission(permissions.BasePermission):
    message = _('Operation not allowed.')

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
