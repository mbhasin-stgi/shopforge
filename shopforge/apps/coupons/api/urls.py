"""Coupons API URL configuration."""

from django.urls import path

from shopforge.apps.coupons.api.views import CouponValidateView

app_name = "coupons"

urlpatterns = [
    path("validate/", CouponValidateView.as_view(), name="coupon-validate"),
]
