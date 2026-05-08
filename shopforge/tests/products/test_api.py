"""Tests for the Products API endpoints."""

from decimal import Decimal

import pytest
from model_bakery import baker

from django.urls import reverse


@pytest.mark.django_db
class TestProductListAPI:
    """Tests for GET /api/products/"""

    url = reverse("api:products:product-list")

    def test_list_returns_active_products(self, api_client, product):
        """Unauthenticated users see only active products."""
        draft = baker.make("products.Product", status="DRAFT", category=product.category)

        response = api_client.get(self.url)

        assert response.status_code == 200
        slugs = [p["slug"] for p in response.data["results"]]
        assert product.slug in slugs
        assert draft.slug not in slugs

    def test_admin_sees_all_products(self, admin_client, product):
        """Admin users see all products including drafts."""
        draft = baker.make("products.Product", status="DRAFT", category=product.category)

        response = admin_client.get(self.url)

        slugs = [p["slug"] for p in response.data["results"]]
        assert product.slug in slugs
        assert draft.slug in slugs

    def test_filter_by_category(self, api_client, product, category):
        """Products can be filtered by category slug."""
        other_cat = baker.make("products.Category", slug="clothing")
        baker.make("products.Product", category=other_cat, status="ACTIVE")

        response = api_client.get(self.url, {"category": "electronics"})

        assert response.status_code == 200
        assert all(p["category_name"] == "Electronics" for p in response.data["results"])

    def test_search_by_name(self, api_client, product):
        """Products can be searched by name."""
        response = api_client.get(self.url, {"search": "wireless"})

        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_price_range_filter(self, api_client, product):
        """Products can be filtered by price range."""
        response = api_client.get(self.url, {"min_price": "50", "max_price": "100"})

        assert response.status_code == 200
        for p in response.data["results"]:
            assert Decimal("50") <= Decimal(p["price"]) <= Decimal("100")


@pytest.mark.django_db
class TestProductCreateAPI:
    """Tests for POST /api/products/"""

    url = reverse("api:products:product-list")

    def test_unauthenticated_cannot_create(self, api_client):
        """Anonymous users get 403 on POST."""
        response = api_client.post(self.url, {})
        assert response.status_code == 403

    def test_regular_user_cannot_create(self, authenticated_client):
        """Regular users get 403 on POST."""
        response = authenticated_client.post(self.url, {})
        assert response.status_code == 403

    def test_admin_can_create_product(self, admin_client, category):
        """Admin can create a new product."""
        data = {
            "name": "New Widget",
            "description": "A fantastic widget.",
            "sku": "NW-001",
            "price": "29.99",
            "category_id": category.id,
            "status": "DRAFT",
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 201
        assert response.data["name"] == "New Widget"
        assert response.data["slug"] == "new-widget"


@pytest.mark.django_db
class TestProductFeaturedAPI:
    """Tests for GET /api/products/featured/"""

    url = reverse("api:products:product-featured")

    def test_returns_featured_products(self, api_client, product):
        """Featured endpoint returns only featured active products."""
        non_featured = baker.make(
            "products.Product",
            is_featured=False,
            status="ACTIVE",
            category=product.category,
        )

        response = api_client.get(self.url)

        assert response.status_code == 200
        slugs = [p["slug"] for p in response.data]
        assert product.slug in slugs
        assert non_featured.slug not in slugs
