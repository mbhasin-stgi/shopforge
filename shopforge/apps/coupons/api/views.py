"""Coupon API views."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shopforge.apps.coupons.api.serializers import CouponValidateResponseSerializer, CouponValidateSerializer
from shopforge.apps.coupons.services import CouponService


class CouponValidateView(APIView):
    """
    POST /api/coupons/validate/

    Validates a coupon code against a given subtotal and returns the discount
    amount. Read-only — does not apply the coupon or record any usage.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        subtotal = serializer.validated_data["subtotal"]

        try:
            coupon, discount = CouponService.validate(code, request.user, subtotal)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response = CouponValidateResponseSerializer(
            {
                "code": coupon.code,
                "discount_type": coupon.discount_type,
                "discount_value": coupon.discount_value,
                "discount_amount": discount,
                "description": coupon.description,
            }
        )
        return Response(response.data)
