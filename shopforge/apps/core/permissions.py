"""
Shared permission classes for the API.

Corporate pattern: Define permissions at the platform level,
not per-app. This ensures consistent access control.
"""

from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Allow read access to anyone, write access only to admins.

    Use for: Product catalog (anyone browses, admins manage)
    """

    def has_permission(self, request, view):
        """Check if request is read-only or user is admin."""
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: only the owner or admin can modify.

    Use for: Orders (customers see their own, admins see all)
    """

    def has_object_permission(self, request, view, obj):
        """Check if user owns the object or is admin."""
        if request.user.is_staff:
            return True
        # Check for 'customer' or 'user' field
        owner = getattr(obj, "customer", None) or getattr(obj, "user", None)
        return owner == request.user
