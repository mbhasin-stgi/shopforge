"""
Product catalog models.

Hierarchy:
  Category → Product → ProductImage
              ↓
         ProductVariant (size, color, etc.)
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from shopforge.apps.core.models import SoftDeleteManager, SoftDeleteModel, TimeStampedModel, UUIDModel


class Category(TimeStampedModel):
    """
    Product category with hierarchical support (parent/child).

    Examples: Electronics > Phones > Smartphones
    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["parent", "is_active"]),
        ]

    def __str__(self):
        """Return category name with parent path."""
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductManager(SoftDeleteManager):
    """Custom manager for Product queryset operations."""

    def active(self):
        """Return only active, published products."""
        return self.filter(status=Product.Status.ACTIVE)

    def featured(self):
        """Return featured products for homepage display."""
        return self.active().filter(is_featured=True)


class Product(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """
    The core product model.

    Uses UUID primary key (secure URLs), timestamps (audit),
    and soft-delete (never lose product data).
    """

    class Status(models.TextChoices):
        """Product lifecycle status."""

        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"
        OUT_OF_STOCK = "OUT_OF_STOCK", "Out of Stock"

    # Basic info
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField(help_text="Full product description (supports markdown)")
    short_description = models.CharField(max_length=500, blank=True)

    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # Can't delete a category that has products
        related_name="products",
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Current selling price",
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price (for showing discounts)",
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost to acquire/produce (for margin calculations)",
    )

    # Metadata
    sku = models.CharField("SKU", max_length=100, unique=True, help_text="Stock Keeping Unit")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in kg")

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    # Custom manager
    objects = ProductManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["status", "is_featured"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self):
        """Return product name with SKU."""
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        """Auto-generate slug from name."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_on_sale(self):
        """Check if product has an active discount."""
        return self.compare_at_price is not None and self.compare_at_price > self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if not self.is_on_sale:
            return 0
        return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)

    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if not self.cost_price or self.cost_price == 0:
            return None
        return ((self.price - self.cost_price) / self.price) * 100


class ProductImage(TimeStampedModel):
    """
    Product images with ordering support.

    Separated from Product because:
    1. A product can have many images (one-to-many)
    2. Images can be reordered without touching the product record
    3. Different sizes/formats can be generated independently
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/%Y/%m/")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Accessibility alt text")
    display_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        """Return image info."""
        return f"Image for {self.product.name} (#{self.display_order})"
