from django.contrib.auth.models import PermissionsMixin
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrContentManagerOrReadOnly(BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        if request.user.groups.filter(name="Контент-менеджер").exists():
            return True

        return False
