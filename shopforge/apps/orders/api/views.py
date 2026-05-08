"""Order API views."""

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
        Create a new order.

        This is where the "thin view" principle gets tested. The view:
        1. Validates input (serializer)
        2. Calls the business logic (inline here, could be a service)
        3. Returns the result

        In a larger project, step 2 would be: OrderService.create_order(validated_data)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        items_data = data.pop("items")

        # Create the order
        order = Order.objects.create(customer=request.user, **data)

        # Create order items with price snapshots
        for item_data in items_data:
            product = Product.objects.get(id=item_data["product_id"])
            order.items.create(
                product=product,
                product_name=product.name,
                product_sku=product.sku,
                price_at_purchase=product.price,
                quantity=item_data["quantity"],
            )

        # Calculate totals
        order.calculate_totals()

        # ─── Async tasks ────────────────────────────
        # These run in the background AFTER the response is sent

        from shopforge.apps.inventory.tasks import reserve_stock_for_order
        from shopforge.apps.orders.tasks import send_order_confirmation_email

        send_order_confirmation_email.delay(str(order.id))
        reserve_stock_for_order.delay(str(order.id))

        # Return the created order
        output_serializer = OrderDetailSerializer(order, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        """Cancel an order (only if still pending)."""
        order = self.get_object()
        if order.status != Order.Status.PENDING:
            return Response(
                {"error": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderDetailSerializer(order, context={"request": request}).data)
