"""Tests for core permission classes."""

import pytest
from model_bakery import baker

from rest_framework.test import APIRequestFactory

from shopforge.apps.core.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.mark.django_db
class TestIsAdminOrReadOnly:
    """IsAdminOrReadOnly: safe methods allowed for all, write methods admin-only."""

    def test_get_allowed_for_anonymous(self, factory):
        request = factory.get("/")
        request.user = baker.prepare("users.User", is_staff=False)
        perm = IsAdminOrReadOnly()
        assert perm.has_permission(request, None) is True

    def test_post_denied_for_non_admin(self, factory):
        request = factory.post("/")
        request.user = baker.prepare("users.User", is_staff=False)
        perm = IsAdminOrReadOnly()
        assert perm.has_permission(request, None) is False

    def test_post_allowed_for_admin(self, factory, admin_user):
        request = factory.post("/")
        request.user = admin_user
        perm = IsAdminOrReadOnly()
        assert perm.has_permission(request, None) is True

    def test_delete_allowed_for_admin(self, factory, admin_user):
        request = factory.delete("/")
        request.user = admin_user
        perm = IsAdminOrReadOnly()
        assert perm.has_permission(request, None) is True


@pytest.mark.django_db
class TestIsOwnerOrAdmin:
    """IsOwnerOrAdmin: owner and admin can access objects; others cannot."""

    def test_owner_can_access(self, factory, user, order):
        request = factory.get("/")
        request.user = user
        perm = IsOwnerOrAdmin()
        assert perm.has_object_permission(request, None, order) is True

    def test_admin_can_access_any_order(self, factory, admin_user, order):
        request = factory.get("/")
        request.user = admin_user
        perm = IsOwnerOrAdmin()
        assert perm.has_object_permission(request, None, order) is True

    def test_other_user_denied(self, factory, order):
        other = baker.make("users.User", email="other@test.com", is_active=True)
        request = factory.get("/")
        request.user = other
        perm = IsOwnerOrAdmin()
        assert perm.has_object_permission(request, None, order) is False
