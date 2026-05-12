"""Wishlist API views."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from shopforge.apps.wishlist.api.serializers import WishlistAddSerializer, WishlistItemSerializer
from shopforge.apps.wishlist.models import Wishlist, WishlistItem


class WishlistViewSet(GenericViewSet):
    """
    Wishlist management.

    list:   GET /api/wishlist/        — return current user's wishlist items
    add:    POST /api/wishlist/add/   — add a product
    remove: DELETE /api/wishlist/{item_id}/remove/ — remove an item
    clear:  DELETE /api/wishlist/     — remove all items
    """

    permission_classes = [IsAuthenticated]

    def _get_wishlist(self) -> Wishlist:
        wishlist, _ = Wishlist.objects.get_or_create(owner=self.request.user)
        return wishlist

    def list(self, request):
        wishlist = self._get_wishlist()
        items = WishlistItem.objects.filter(wishlist=wishlist).select_related("product")
        return Response(WishlistItemSerializer(items, many=True, context={"request": request}).data)

    @action(detail=False, methods=["post"], url_path="add")
    def add(self, request):
        """Add a product to the wishlist (idempotent)."""
        serializer = WishlistAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product_id"]
        wishlist = self._get_wishlist()
        item, _ = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        return Response(
            WishlistItemSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["delete"], url_path="remove")
    def remove(self, request, pk=None):
        """Remove a specific item from the wishlist."""
        wishlist = self._get_wishlist()
        deleted, _ = WishlistItem.objects.filter(id=pk, wishlist=wishlist).delete()
        if not deleted:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["delete"], url_path="clear")
    def clear(self, request):
        """Remove all items from the wishlist."""
        wishlist = self._get_wishlist()
        wishlist.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
