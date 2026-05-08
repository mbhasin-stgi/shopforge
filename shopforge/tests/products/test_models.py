"""Tests for Product models."""

from decimal import Decimal

import pytest
from model_bakery import baker

from shopforge.apps.products.models import Product


@pytest.mark.django_db
class TestCategory:
    """Tests for the Category model."""

    def test_str_representation(self, category):
        """Category __str__ returns name."""
        assert str(category) == "Electronics"

    def test_str_with_parent(self, category):
        """Child category shows full path."""
        child = baker.make("products.Category", name="Phones", parent=category)
        assert str(child) == "Electronics > Phones"

    def test_auto_slug_generation(self):
        """Slug is auto-generated from name on save."""
        cat = baker.make("products.Category", name="Smart Home Devices", slug="")
        cat.save()
        assert cat.slug == "smart-home-devices"


@pytest.mark.django_db
class TestProduct:
    """Tests for the Product model."""

    def test_str_representation(self, product):
        """Product __str__ returns name and SKU."""
        assert str(product) == "Wireless Headphones (WH-001)"

    def test_active_manager(self, product):
        """Product.objects.active() returns only active products."""
        draft = baker.make("products.Product", status="DRAFT", category=product.category)
        active_products = Product.objects.active()
        assert product in active_products
        assert draft not in active_products

    def test_is_on_sale(self, product):
        """Product correctly detects sale status."""
        product.compare_at_price = Decimal("99.99")
        product.save()
        assert product.is_on_sale is True

    def test_not_on_sale(self, product):
        """Product without compare_at_price is not on sale."""
        assert product.is_on_sale is False

    def test_discount_percentage(self, product):
        """Discount percentage calculated correctly."""
        product.price = Decimal("75.00")
        product.compare_at_price = Decimal("100.00")
        product.save()
        assert product.discount_percentage == 25

    def test_soft_delete(self, product):
        """Soft-deleted products don't appear in default queryset."""
        product.soft_delete()
        assert Product.objects.filter(id=product.id).count() == 0
        assert Product.all_objects.filter(id=product.id).count() == 1

    def test_restore_soft_deleted(self, product):
        """Restoring a soft-deleted product makes it visible again."""
        product.soft_delete()
        product.restore()
        assert Product.objects.filter(id=product.id).count() == 1
