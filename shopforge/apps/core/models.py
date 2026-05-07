"""
Core abstract models for ShopForge.

These provide common fields and behaviors that most models need.
Think of them as the "DNA" that all your models inherit.
"""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating `created_at` and `updated_at` fields.

    Every model in a corporate app needs these. They answer:
    - "When was this record first created?" (audit trail)
    - "When was it last modified?" (cache invalidation, debugging)
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was first created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last modified.",
    )

    class Meta:
        abstract = True  # This model won't create a database table
        ordering = ["-created_at"]  # Newest first by default


class UUIDModel(models.Model):
    """
    Abstract base model that uses UUID as the primary key.

    Benefits over auto-incrementing integers:
    - Can't be guessed (security: users can't enumerate /api/orders/1, /api/orders/2...)
    - Can be generated client-side (useful for offline-first apps)
    - Safe for distributed systems (no central ID counter needed)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default."""

    def get_queryset(self):
        """Return only non-deleted records."""
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Manager that includes ALL records, even soft-deleted ones."""

    pass


class SoftDeleteModel(models.Model):
    """
    Abstract base model for soft-delete behavior.

    Instead of actually deleting records (which loses data forever),
    we mark them as deleted. Benefits:
    - Undo accidental deletions
    - Audit trail (who deleted what, when)
    - Foreign key integrity (no dangling references)
    - Data recovery for compliance/legal requirements
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Default manager excludes deleted records
    objects = SoftDeleteManager()
    # Use this when you explicitly need deleted records too
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark this record as deleted without removing it from the database."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])