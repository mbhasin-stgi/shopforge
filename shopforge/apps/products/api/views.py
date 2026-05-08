"""
Product API views.

Corporate pattern: Views are THIN. They handle:
- Which serializer to use
- Which queryset to return
- Which permissions to check

They do NOT handle business logic. That belongs in services or model methods.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from shopforge.apps.core.permissions import IsAdminOrReadOnly
from shopforge.apps.products.models import Category, Product

from .filters import ProductFilter
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product categories.

    list:   GET /api/products/categories/
    create: POST /api/products/categories/       (admin only)
    detail: GET /api/products/categories/{id}/
    update: PUT /api/products/categories/{id}/   (admin only)
    delete: DELETE /api/products/categories/{id}/ (admin only)
    """

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "display_order", "created_at"]


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products.

    list:     GET /api/products/                 (with filtering, search, pagination)
    create:   POST /api/products/                (admin only)
    detail:   GET /api/products/{id}/
    update:   PUT /api/products/{id}/            (admin only)
    delete:   DELETE /api/products/{id}/          (admin only)
    featured: GET /api/products/featured/         (custom action)
    """

    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["price", "name", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Use different serializers for list vs detail views."""
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        """
        Return appropriate queryset based on user.

        - Admin: sees all products (including drafts)
        - Everyone else: sees only active products
        """
        if self.request.user.is_staff:
            return Product.objects.select_related("category").prefetch_related("images")
        return Product.objects.active().select_related("category").prefetch_related("images")

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Return featured products for homepage display."""
        products = Product.objects.featured()[:12]
        serializer = ProductListSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)