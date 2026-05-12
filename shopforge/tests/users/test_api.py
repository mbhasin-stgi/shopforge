"""Tests for Users API endpoints."""

import pytest
from model_bakery import baker


@pytest.mark.django_db
class TestUserProfileView:
    """GET/PATCH /api/users/me/"""

    def test_get_profile_authenticated(self, authenticated_client, user):
        response = authenticated_client.get("/api/users/me/")
        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get("/api/users/me/")
        assert response.status_code == 403

    def test_patch_profile_updates_name(self, authenticated_client, user):
        response = authenticated_client.patch(
            "/api/users/me/",
            {"first_name": "Alice", "last_name": "Smith"},
            format="json",
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "Alice"
        assert user.last_name == "Smith"

    def test_patch_does_not_update_email(self, authenticated_client, user):
        """Email field should be read-only in the profile serializer."""
        original_email = user.email
        authenticated_client.patch(
            "/api/users/me/",
            {"email": "hacked@evil.com"},
            format="json",
        )
        user.refresh_from_db()
        assert user.email == original_email

    def test_another_user_cannot_access_profile(self, api_client, admin_user):
        """Each user can only access their own profile."""
        other = baker.make("users.User", email="other@shopforge.test", is_active=True)
        api_client.force_authenticate(user=other)
        response = api_client.get("/api/users/me/")
        assert response.status_code == 200
        assert response.data["email"] == other.email
