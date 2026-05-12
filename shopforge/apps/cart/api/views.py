"""Cart API views."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from shopforge.apps.cart.api.serializers import (
    CartCheckoutSerializer,
    CartItemAddSerializer,
    CartItemUpdateSerializer,
    CartSerializer,
)
from shopforge.apps.cart.services import CartService


class CartViewSet(GenericViewSet):
    """
    Cart management endpoint.

    retrieve:  GET  /api/cart/            — return the current user's cart
    add:       POST /api/cart/add/        — add a product to the cart
    update:    PATCH /api/cart/items/{id}/ — change quantity (0 = remove)
    remove:    DELETE /api/cart/items/{id}/ — remove item
    clear:     DELETE /api/cart/          — empty the cart
    checkout:  POST /api/cart/checkout/   — convert cart to an order
    """

    permission_classes = [IsAuthenticated]

    def _get_cart(self):
        return CartService.get_or_create_for_user(self.request.user)

    def list(self, request, *args, **kwargs):
        """Return the authenticated user's cart (GET /api/cart/)."""
        cart = self._get_cart()
        return Response(CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"], url_path="add")
    def add(self, request):
        """Add a product to the cart (or increment quantity if already present)."""
        serializer = CartItemAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        cart = self._get_cart()
        CartService.add_item(cart, product, quantity)
        return Response(
            CartSerializer(cart, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="items/(?P<item_id>[^/.]+)")
    def update_item(self, request, item_id=None):
        """Update the quantity of a specific cart item. Set quantity=0 to remove."""
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["quantity"]

        cart = self._get_cart()
        try:
            from shopforge.apps.cart.models import CartItem

            item = CartItem.objects.get(id=item_id, cart=cart)
        except Exception:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        if quantity == 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save(update_fields=["quantity", "updated_at"])

        return Response(CartSerializer(cart, context={"request": request}).data)

    @action(detail=True, methods=["delete"], url_path="items/(?P<item_id>[^/.]+)/remove")
    def remove_item(self, request, item_id=None):
        """Remove a specific item from the cart."""
        cart = self._get_cart()
        try:
            from shopforge.apps.cart.models import CartItem

            item = CartItem.objects.get(id=item_id, cart=cart)
        except Exception:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["delete"], url_path="clear")
    def clear(self, request):
        """Empty the cart."""
        cart = self._get_cart()
        CartService.clear(cart)
        return Response(CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        """
        Convert the current cart into an order.

        Validates stock, applies coupon if provided, creates the Order + OrderItems
        (via OrderService), clears the cart, and fires confirmation email.
        """
        cart = self._get_cart()
        if not cart.items.exists():
            return Response({"error": "Cannot checkout an empty cart."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        CartService.refresh_prices(cart)

        from shopforge.apps.orders.services import OrderService

        try:
            order = OrderService.create_from_cart(
                cart=cart,
                customer=request.user,
                shipping_data=serializer.validated_data,
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        CartService.clear(cart)

        from shopforge.apps.orders.api.serializers import OrderDetailSerializer

        return Response(
            OrderDetailSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
