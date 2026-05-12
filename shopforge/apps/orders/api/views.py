"""Order API views."""

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from shopforge.apps.core.permissions import IsOwnerOrAdmin
from shopforge.apps.orders.models import Order
from shopforge.apps.products.models import Product

from .serializers import OrderCreateSerializer, OrderDetailSerializer, OrderListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders.

    Customers see only their own orders.
    Admins see all orders.
    """

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    http_method_names = ["get", "post", "patch", "head", "options"]  # No PUT or DELETE

    def get_serializer_class(self):
        """Use appropriate serializer for each action."""
        if self.action == "list":
            return OrderListSerializer
        if self.action == "create":
            return OrderCreateSerializer
        return OrderDetailSerializer

    def get_queryset(self):
        """Filter orders based on user role."""
        if self.request.user.is_staff:
            return Order.objects.prefetch_related("items").all()
        return Order.objects.prefetch_related("items").filter(customer=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new order via OrderService (atomic stock check + reservation).

        The service handles: stock locking, item creation, inventory reservation,
        total calculation, and async confirmation email via on_commit hook.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        items_data_raw = data.pop("items")

        # Resolve product UUIDs to Product instances
        items_data = [
            {
                "product": Product.objects.get(id=entry["product_id"]),
                "quantity": entry["quantity"],
            }
            for entry in items_data_raw
        ]

        from shopforge.apps.orders.services import OrderService

        try:
            order = OrderService.create_order(
                customer=request.user,
                items_data=items_data,
                shipping_data=data,
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = OrderDetailSerializer(order, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        """
        Cancel a pending order.

        Only orders in PENDING status can be cancelled by the customer.
        Staff can cancel orders in PENDING or CONFIRMED status.
        Stock release is handled automatically by the pre_save signal in orders/signals.py.
        """
        order = self.get_object()

        cancellable_statuses = {Order.Status.PENDING}
        if request.user.is_staff:
            cancellable_statuses.add(Order.Status.CONFIRMED)

        if order.status not in cancellable_statuses:
            return Response(
                {"error": f"Orders with status '{order.get_status_display()}' cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status", "updated_at"])

        return Response(OrderDetailSerializer(order, context={"request": request}).data)
