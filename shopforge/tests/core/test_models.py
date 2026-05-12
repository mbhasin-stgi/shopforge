"""Tests for core abstract models."""

import pytest
from model_bakery import baker


@pytest.mark.django_db
class TestSoftDeleteModel:
    """Tests for SoftDeleteModel functionality."""

    def test_soft_delete_sets_is_deleted(self, product):
        """soft_delete() sets is_deleted=True without removing the DB row."""
        product.soft_delete()
        product.refresh_from_db()
        assert product.is_deleted is True
        assert product.deleted_at is not None

    def test_soft_delete_excluded_from_default_manager(self, product):
        """Soft-deleted products are excluded from the default manager."""
        from shopforge.apps.products.models import Product

        product.soft_delete()
        assert not Product.objects.filter(pk=product.pk).exists()

    def test_restore_undeletes_product(self, product):
        """restore() clears is_deleted and deleted_at."""
        product.soft_delete()
        product.restore()
        product.refresh_from_db()
        assert product.is_deleted is False
        assert product.deleted_at is None

    def test_all_objects_includes_soft_deleted(self, product):
        """all_objects manager returns soft-deleted records."""
        from shopforge.apps.products.models import Product

        product.soft_delete()
        assert Product.all_objects.filter(pk=product.pk).exists()

    def test_soft_deleted_at_timestamp_preserved(self, product):
        """deleted_at timestamp is set at deletion time."""
        from django.utils import timezone

        before = timezone.now()
        product.soft_delete()
        after = timezone.now()
        product.refresh_from_db()
        assert before <= product.deleted_at <= after


@pytest.mark.django_db
class TestUUIDModel:
    """Tests for UUIDModel primary key."""

    def test_uuid_pk_is_set(self, product):
        """Products use a UUID as primary key."""
        import uuid

        assert isinstance(product.id, uuid.UUID)

    def test_different_instances_have_different_uuids(self, category):
        """Two separately created products have different UUIDs."""
        from shopforge.apps.products.models import Product

        p1 = baker.make(Product, category=category, sku="SKU-A", slug="sku-a")
        p2 = baker.make(Product, category=category, sku="SKU-B", slug="sku-b")
        assert p1.id != p2.id


@pytest.mark.django_db
class TestTimeStampedModel:
    """Tests for TimeStampedModel auto timestamps."""

    def test_created_at_set_on_save(self, product):
        assert product.created_at is not None

    def test_updated_at_changes_on_update(self, product):
        before = product.updated_at
        import time

        time.sleep(0.01)  # noqa: E702
        product.name = "Updated name"
        product.save(update_fields=["name", "updated_at"])
        product.refresh_from_db()
        # updated_at should be >= before
        assert product.updated_at >= before
