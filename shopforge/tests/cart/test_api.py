"""Tests for Cart API endpoints and CartService."""

import pytest


@pytest.mark.django_db
class TestCartViewSet:
    """Tests for GET/POST/DELETE cart endpoints."""

    def test_retrieve_cart_creates_if_missing(self, authenticated_client):
        """GET /api/cart/ creates a cart for the user if they don't have one."""
        response = authenticated_client.get("/api/cart/")
        assert response.status_code == 200
        assert response.data["item_count"] == 0

    def test_retrieve_cart_requires_auth(self, api_client):
        response = api_client.get("/api/cart/")
        assert response.status_code == 403

    def test_add_item_to_cart(self, authenticated_client, product_with_stock):
        response = authenticated_client.post(
            "/api/cart/add/",
            {"product_id": str(product_with_stock.id), "quantity": 2},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["item_count"] == 2

    def test_add_same_item_increments_quantity(self, authenticated_client, product_with_stock):
        authenticated_client.post(
            "/api/cart/add/",
            {"product_id": str(product_with_stock.id), "quantity": 1},
            format="json",
        )
        authenticated_client.post(
            "/api/cart/add/",
            {"product_id": str(product_with_stock.id), "quantity": 2},
            format="json",
        )
        response = authenticated_client.get("/api/cart/")
        assert response.data["item_count"] == 3

    def test_add_inactive_product_rejected(self, authenticated_client, product):
        product.status = "ARCHIVED"
        product.save(update_fields=["status"])
        response = authenticated_client.post(
            "/api/cart/add/",
            {"product_id": str(product.id), "quantity": 1},
            format="json",
        )
        assert response.status_code == 400

    def test_clear_cart(self, authenticated_client, product_with_stock):
        authenticated_client.post(
            "/api/cart/add/",
            {"product_id": str(product_with_stock.id), "quantity": 1},
            format="json",
        )
        response = authenticated_client.delete("/api/cart/clear/")
        assert response.status_code == 200
        assert response.data["item_count"] == 0


@pytest.mark.django_db
class TestCartService:
    """Unit tests for CartService operations."""

    def test_get_or_create_for_user(self, user):
        from shopforge.apps.cart.services import CartService

        cart = CartService.get_or_create_for_user(user)
        assert cart.owner == user

    def test_add_item_snapshots_price(self, user, product_with_stock):
        from shopforge.apps.cart.services import CartService

        cart = CartService.get_or_create_for_user(user)
        item = CartService.add_item(cart, product_with_stock, 2)
        assert item.price_snapshot == product_with_stock.price
        assert item.quantity == 2

    def test_remove_item(self, user, product_with_stock):
        from shopforge.apps.cart.models import CartItem
        from shopforge.apps.cart.services import CartService

        cart = CartService.get_or_create_for_user(user)
        CartService.add_item(cart, product_with_stock, 1)
        CartService.remove_item(cart, product_with_stock)
        assert not CartItem.objects.filter(cart=cart, product=product_with_stock).exists()

    def test_cart_total(self, user, product_with_stock):
        from shopforge.apps.cart.services import CartService

        cart = CartService.get_or_create_for_user(user)
        CartService.add_item(cart, product_with_stock, 3)
        expected = product_with_stock.price * 3
        assert cart.total == expected

    def test_merge_session_cart(self, user, product_with_stock):
        """Session cart items are merged into the user cart on login."""
        from shopforge.apps.cart.models import Cart
        from shopforge.apps.cart.services import CartService

        session_cart = Cart.objects.create(session_key="test-session-123")
        CartService.add_item(session_cart, product_with_stock, 2)
        user_cart = CartService.merge_session_cart_into_user("test-session-123", user)
        item = user_cart.items.get(product=product_with_stock)
        assert item.quantity == 2
        assert not Cart.objects.filter(session_key="test-session-123").exists()
