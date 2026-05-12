"""Tests for Review API endpoints."""

import pytest
from model_bakery import baker


@pytest.mark.django_db
class TestReviewListCreate:
    """GET/POST /api/products/{slug}/reviews/"""

    def test_list_approved_reviews(self, api_client, product):
        from shopforge.apps.reviews.models import Review

        baker.make(Review, product=product, rating=4, is_approved=True)
        baker.make(Review, product=product, rating=2, is_approved=False)
        response = api_client.get(f"/api/products/{product.slug}/reviews/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_create_review_authenticated(self, authenticated_client, product):
        response = authenticated_client.post(
            f"/api/products/{product.slug}/reviews/",
            {"rating": 5, "title": "Great!", "body": "Excellent product."},
            format="json",
        )
        assert response.status_code == 201

    def test_create_review_unauthenticated_rejected(self, api_client, product):
        response = api_client.post(
            f"/api/products/{product.slug}/reviews/",
            {"rating": 3, "body": "Decent."},
            format="json",
        )
        assert response.status_code == 403

    def test_duplicate_review_rejected(self, authenticated_client, user, product):
        from shopforge.apps.reviews.models import Review

        baker.make(Review, product=product, author=user, rating=3, is_approved=True)
        response = authenticated_client.post(
            f"/api/products/{product.slug}/reviews/",
            {"rating": 4, "body": "Second review attempt."},
            format="json",
        )
        assert response.status_code == 400

    def test_rating_must_be_1_to_5(self, authenticated_client, product):
        response = authenticated_client.post(
            f"/api/products/{product.slug}/reviews/",
            {"rating": 6, "body": "Too high!"},
            format="json",
        )
        assert response.status_code == 400

    def test_verified_purchase_flag(self, authenticated_client, user, product):
        """is_verified_purchase is True when user has a DELIVERED order with the product."""
        from shopforge.apps.orders.models import Order

        delivered_order = baker.make(
            "orders.Order",
            customer=user,
            status=Order.Status.DELIVERED,
        )
        baker.make(
            "orders.OrderItem",
            order=delivered_order,
            product=product,
            quantity=1,
            price_at_purchase=product.price,
            product_name=product.name,
            product_sku=product.sku,
        )
        response = authenticated_client.post(
            f"/api/products/{product.slug}/reviews/",
            {"rating": 5, "body": "Love it!"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["is_verified_purchase"] is True
