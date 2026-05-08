"""
Root conftest.py for shopforge/tests/ — pytest fixtures available to ALL tests.

Fixtures are the "setup" for your tests. Instead of creating users
and products in every test, you define them once here and inject them.
"""

from decimal import Decimal

import pytest
from model_bakery import baker

from rest_framework.test import APIClient

# ─── API Client Fixtures ──────────────────────────────────────────────


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an API client authenticated as a regular user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an API client authenticated as an admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client


# ─── User Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def user(db):
    """Create a regular customer user."""
    return baker.make(
        "users.User",
        email="customer@shopforge.test",
        role="CUSTOMER",
        is_active=True,
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return baker.make(
        "users.User",
        email="admin@shopforge.test",
        role="ADMIN",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )


# ─── Product Fixtures ─────────────────────────────────────────────────


@pytest.fixture
def category(db):
    """Create a product category."""
    return baker.make(
        "products.Category",
        name="Electronics",
        slug="electronics",
        is_active=True,
    )


@pytest.fixture
def product(db, category):
    """Create an active product."""
    return baker.make(
        "products.Product",
        name="Wireless Headphones",
        slug="wireless-headphones",
        sku="WH-001",
        category=category,
        price=Decimal("79.99"),
        status="ACTIVE",
        is_featured=True,
    )


@pytest.fixture
def product_with_stock(product):
    """Create a product with stock record."""
    baker.make(
        "inventory.StockRecord",
        product=product,
        quantity=100,
        reserved_quantity=5,
        reorder_level=10,
    )
    return product


# ─── Order Fixtures ───────────────────────────────────────────────────


@pytest.fixture
def order(db, user, product):
    """Create a pending order with one item."""
    order = baker.make(
        "orders.Order",
        customer=user,
        order_number="SF-1234567",
        status="PENDING",
        shipping_address_line1="123 Test St",
        shipping_city="Testville",
        shipping_state="TS",
        shipping_postal_code="12345",
    )
    baker.make(
        "orders.OrderItem",
        order=order,
        product=product,
        product_name=product.name,
        product_sku=product.sku,
        price_at_purchase=product.price,
        quantity=2,
    )
    order.calculate_totals()
    return order
