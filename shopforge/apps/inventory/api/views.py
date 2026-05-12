"""Inventory API views (admin only)."""

from rest_framework import filters, mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from shopforge.apps.inventory.models import StockMovement, StockRecord
from shopforge.apps.inventory.services import InventoryService


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for stock movement audit records."""

    movement_type_display = serializers.CharField(source="get_movement_type_display", read_only=True)
    performed_by_email = serializers.EmailField(source="performed_by.email", read_only=True, default=None)

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "movement_type",
            "movement_type_display",
            "quantity_change",
            "reference",
            "notes",
            "performed_by_email",
            "created_at",
        ]


class StockRecordSerializer(serializers.ModelSerializer):
    """Serializer for stock records."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model = StockRecord
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "reorder_level",
            "reorder_quantity",
            "needs_reorder",
            "updated_at",
        ]
        read_only_fields = ["reserved_quantity", "updated_at"]


class StockAdjustSerializer(serializers.Serializer):
    """Input for a manual stock adjustment."""

    delta = serializers.IntegerField(help_text="Positive = stock in, negative = stock out.")
    notes = serializers.CharField(max_length=500)


class StockRecordViewSet(viewsets.ModelViewSet):
    """
    Admin-only stock management endpoint.

    list:     GET /api/inventory/
    retrieve: GET /api/inventory/{id}/
    update:   PATCH /api/inventory/{id}/         — update reorder levels etc.
    adjust:   POST /api/inventory/{id}/adjust/   — manual stock adjustment
    movements: GET /api/inventory/{id}/movements/ — audit log
    """

    serializer_class = StockRecordSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product__name", "product__sku"]
    ordering_fields = ["product__name", "quantity", "updated_at"]

    def get_queryset(self):
        return StockRecord.objects.select_related("product").all()

    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        """Apply a manual stock adjustment with an audit note."""
        stock = self.get_object()
        serializer = StockAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            InventoryService.adjust(
                stock_record=stock,
                delta=serializer.validated_data["delta"],
                notes=serializer.validated_data["notes"],
                performed_by=request.user,
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)

        stock.refresh_from_db()
        return Response(StockRecordSerializer(stock).data)

    @action(detail=True, methods=["get"])
    def movements(self, request, pk=None):
        """Return the audit log of stock movements for this product."""
        stock = self.get_object()
        qs = stock.movements.order_by("-created_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(StockMovementSerializer(page, many=True).data)
        return Response(StockMovementSerializer(qs, many=True).data)


class StockMovementViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Read-only global stock movement log (admin only)."""

    serializer_class = StockMovementSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reference", "stock_record__product__name"]
    ordering_fields = ["created_at", "movement_type"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return StockMovement.objects.select_related("stock_record__product", "performed_by").all()
