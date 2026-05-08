"""Tests for the Orders API endpoints."""

from unittest.mock import patch

import pytest
from model_bakery import baker

from django.urls import reverse


@pytest.mark.django_db
class TestOrderCreateAPI:
    """Tests for POST /api/orders/"""

    url = reverse("api:orders:order-list")

    def test_unauthenticated_cannot_create_order(self, api_client):
        """Anonymous users cannot create orders — returns 403 with SessionAuthentication."""
        response = api_client.post(self.url, {})
        assert response.status_code == 403

    def test_create_order_success(self, authenticated_client, product_with_stock):
        """Authenticated user can create an order."""
        data = {
            "items": [{"product_id": str(product_with_stock.id), "quantity": 2}],
            "shipping_address_line1": "456 Oak Ave",
            "shipping_city": "Portland",
            "shipping_state": "OR",
            "shipping_postal_code": "97201",
        }

        with (
            patch("shopforge.apps.orders.tasks.send_order_confirmation_email.delay"),
            patch("shopforge.apps.inventory.tasks.reserve_stock_for_order.delay"),
        ):
            response = authenticated_client.post(self.url, data, format="json")

        assert response.status_code == 201
        assert response.data["order_number"].startswith("SF-")
        assert len(response.data["items"]) == 1
        assert response.data["items"][0]["quantity"] == 2

    def test_create_order_empty_items(self, authenticated_client):
        """Order with no items is rejected."""
        data = {
            "items": [],
            "shipping_address_line1": "456 Oak Ave",
            "shipping_city": "Portland",
            "shipping_state": "OR",
            "shipping_postal_code": "97201",
        }

        response = authenticated_client.post(self.url, data, format="json")

        assert response.status_code == 400

    def test_users_see_only_own_orders(self, authenticated_client, user, order):
        """Users only see their own orders in the list."""
        other_user = baker.make("users.User", email="other@test.com")
        baker.make("orders.Order", customer=other_user)

        response = authenticated_client.get(self.url)

        assert response.status_code == 200
        assert all(o["order_number"] == order.order_number for o in response.data["results"])
