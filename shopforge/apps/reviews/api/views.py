"""Review API views nested under products."""

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from shopforge.apps.products.models import Product
from shopforge.apps.reviews.api.serializers import ReviewCreateSerializer, ReviewSerializer
from shopforge.apps.reviews.models import Review


class ReviewViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Reviews nested under a product slug.

    list:   GET /api/products/{slug}/reviews/
    create: POST /api/products/{slug}/reviews/  (authenticated)
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self) -> Product:
        return Product.objects.get(slug=self.kwargs["product_slug"])

    def get_queryset(self):
        return Review.objects.filter(
            product__slug=self.kwargs["product_slug"],
            is_approved=True,
        ).select_related("author")

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def create(self, request, *args, **kwargs):
        """Submit a review. One review per user per product (enforced by unique_together)."""
        product = self.get_product()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if Review.objects.filter(product=product, author=request.user).exists():
            return Response(
                {"error": "You have already reviewed this product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if this is a verified purchase
        is_verified = _is_verified_purchase(request.user, product)
        review = serializer.save(product=product, author=request.user, is_verified_purchase=is_verified)
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


def _is_verified_purchase(user, product) -> bool:
    """Return True if the user has a delivered order containing this product."""
    from shopforge.apps.orders.models import Order

    return Order.objects.filter(
        customer=user,
        status=Order.Status.DELIVERED,
        items__product=product,
    ).exists()
