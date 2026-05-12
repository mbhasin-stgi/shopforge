"""Initial migration for the coupons app."""

import decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("orders", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Coupon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(db_index=True, max_length=50, unique=True)),
                ("description", models.CharField(blank=True, max_length=300)),
                ("discount_type", models.CharField(choices=[("PERCENT", "Percentage Discount"), ("FIXED", "Fixed Amount Discount")], default="PERCENT", max_length=10)),
                ("discount_value", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.01"))])),
                ("min_order_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=10)),
                ("max_uses", models.PositiveIntegerField(blank=True, null=True)),
                ("uses_count", models.PositiveIntegerField(default=0)),
                ("valid_from", models.DateTimeField()),
                ("valid_until", models.DateTimeField()),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CouponUsage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "coupon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usages",
                        to="coupons.coupon",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="coupon_usages",
                        to="orders.order",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="coupon_usages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("discount_applied", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="couponusage",
            unique_together={("coupon", "order")},
        ),
    ]
