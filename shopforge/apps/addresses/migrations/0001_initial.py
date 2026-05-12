"""Initial migration for the addresses app."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserAddress",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False, editable=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("label", models.CharField(blank=True, max_length=100)),
                ("full_name", models.CharField(max_length=200)),
                ("line1", models.CharField(max_length=200, verbose_name="Address line 1")),
                ("line2", models.CharField(blank=True, max_length=200, verbose_name="Address line 2")),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("postal_code", models.CharField(max_length=20)),
                ("country", models.CharField(default="US", max_length=100)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("is_default", models.BooleanField(default=False)),
            ],
            options={"verbose_name": "address", "verbose_name_plural": "addresses", "ordering": ["-is_default", "-created_at"]},
        ),
    ]
