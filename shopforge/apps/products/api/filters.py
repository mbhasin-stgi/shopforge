"""
Product filters for the API.

DjangoFilterBackend uses these classes to add ?field=value query parameters.
Users can filter without us writing custom queryset logic in every view.
"""

import django_filters

from django.db import models

from shopforge.apps.products.models import Product


class ProductFilter(django_filters.FilterSet):
    """Filter products by various criteria."""

    # Range filters
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # Exact match
    category = django_filters.CharFilter(field_name="category__slug")
    status = django_filters.CharFilter(field_name="status")

    # Boolean filters
    is_featured = django_filters.BooleanFilter()
    on_sale = django_filters.BooleanFilter(method="filter_on_sale")

    class Meta:
        model = Product
        fields = ["category", "status", "is_featured"]

    def filter_on_sale(self, queryset, name, value):
        """Filter products that are currently on sale."""
        if value:
            return queryset.filter(compare_at_price__isnull=False, compare_at_price__gt=models.F("price"))
        return queryset
