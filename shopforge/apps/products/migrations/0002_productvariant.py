"""Add ProductVariant model."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variants",
                        to="products.product",
                    ),
                ),
                ("name", models.CharField(help_text="Human-readable variant name, e.g. 'Large / Red'", max_length=200)),
                ("sku", models.CharField(max_length=100, unique=True, verbose_name="SKU")),
                ("price_override", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("attributes", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["product", "name"]},
        ),
        migrations.AddIndex(
            model_name="productvariant",
            index=models.Index(fields=["sku"], name="products_pv_sku_idx"),
        ),
        migrations.AddIndex(
            model_name="productvariant",
            index=models.Index(fields=["product", "is_active"], name="products_pv_product_idx"),
        ),
    ]
