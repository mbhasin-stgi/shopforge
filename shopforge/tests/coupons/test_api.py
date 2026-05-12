"""Tests for Coupons API endpoints and CouponService."""

from datetime import timedelta
from decimal import Decimal

import pytest

from django.utils import timezone


@pytest.fixture
def coupon(db):
    """A valid percentage coupon."""
    from shopforge.apps.coupons.models import Coupon

    return Coupon.objects.create(
        code="SAVE10",
        discount_type=Coupon.DiscountType.PERCENT,
        discount_value=Decimal("10.00"),
        min_order_amount=Decimal("20.00"),
        valid_from=timezone.now() - timedelta(days=1),
        valid_until=timezone.now() + timedelta(days=30),
        is_active=True,
    )


@pytest.fixture
def fixed_coupon(db):
    """A valid fixed-amount coupon."""
    from shopforge.apps.coupons.models import Coupon

    return Coupon.objects.create(
        code="FLAT5",
        discount_type=Coupon.DiscountType.FIXED,
        discount_value=Decimal("5.00"),
        valid_from=timezone.now() - timedelta(days=1),
        valid_until=timezone.now() + timedelta(days=30),
        is_active=True,
    )


@pytest.mark.django_db
class TestCouponValidateView:
    """POST /api/coupons/validate/"""

    def test_valid_percent_coupon(self, authenticated_client, coupon):
        response = authenticated_client.post(
            "/api/coupons/validate/",
            {"code": "SAVE10", "subtotal": "100.00"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["discount_amount"] == "10.00"

    def test_valid_fixed_coupon(self, authenticated_client, fixed_coupon):
        response = authenticated_client.post(
            "/api/coupons/validate/",
            {"code": "FLAT5", "subtotal": "50.00"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["discount_amount"] == "5.00"

    def test_invalid_code_returns_400(self, authenticated_client):
        response = authenticated_client.post(
            "/api/coupons/validate/",
            {"code": "NOTACODE", "subtotal": "50.00"},
            format="json",
        )
        assert response.status_code == 400

    def test_minimum_order_not_met(self, authenticated_client, coupon):
        """Coupon requires $20 minimum; $10 subtotal should fail."""
        response = authenticated_client.post(
            "/api/coupons/validate/",
            {"code": "SAVE10", "subtotal": "10.00"},
            format="json",
        )
        assert response.status_code == 400

    def test_expired_coupon_returns_400(self, authenticated_client):
        from shopforge.apps.coupons.models import Coupon

        Coupon.objects.create(
            code="EXPIRED",
            discount_type=Coupon.DiscountType.PERCENT,
            discount_value=Decimal("5.00"),
            valid_from=timezone.now() - timedelta(days=10),
            valid_until=timezone.now() - timedelta(days=1),
            is_active=True,
        )
        response = authenticated_client.post(
            "/api/coupons/validate/",
            {"code": "EXPIRED", "subtotal": "50.00"},
            format="json",
        )
        assert response.status_code == 400

    def test_unauthenticated_rejected(self, api_client, coupon):
        response = api_client.post(
            "/api/coupons/validate/",
            {"code": "SAVE10", "subtotal": "50.00"},
            format="json",
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestCouponService:
    """Unit tests for CouponService."""

    def test_percentage_discount_calculated_correctly(self, coupon, user):
        from shopforge.apps.coupons.services import CouponService

        _, discount = CouponService.validate("SAVE10", user, Decimal("200.00"))
        assert discount == Decimal("20.00")

    def test_fixed_discount_cannot_exceed_subtotal(self, fixed_coupon, user):
        """A $5 fixed coupon on a $3 order should give $3 discount (not $5)."""
        from shopforge.apps.coupons.services import CouponService

        _, discount = CouponService.validate("FLAT5", user, Decimal("3.00"))
        assert discount == Decimal("3.00")

    def test_max_uses_exhausted_is_invalid(self, user):
        from shopforge.apps.coupons.models import Coupon
        from shopforge.apps.coupons.services import CouponService

        Coupon.objects.create(
            code="LIMITED",
            discount_type=Coupon.DiscountType.FIXED,
            discount_value=Decimal("1.00"),
            max_uses=1,
            uses_count=1,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True,
        )
        with pytest.raises(ValueError):
            CouponService.validate("LIMITED", user, Decimal("50.00"))
