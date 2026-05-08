"""Inventory API views (admin only)."""
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser

from shopforge.apps.inventory.models import StockRecord


class StockRecordSerializer(serializers.ModelSerializer):
    """Serializer for stock records."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model = StockRecord
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "reorder_level",
            "reorder_quantity",
            "needs_reorder",
            "updated_at",
        ]


class StockRecordViewSet(viewsets.ModelViewSet):
    """Admin-only stock management endpoint."""

    queryset = StockRecord.objects.select_related("product").all()
    serializer_class = StockRecordSerializer
    permission_classes = [IsAdminUser]