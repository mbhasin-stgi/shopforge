"""
Admin Dashboard API endpoints.

All endpoints require IsAdminUser. They are registered directly in api_router.py.
These provide the data for an admin frontend dashboard.
"""

from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class DashboardStatsView(APIView):
    """
    GET /api/admin/dashboard/stats/

    Returns high-level revenue and order counts for today, 7d, and 30d windows.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        from shopforge.apps.orders.models import Order

        now = timezone.now()
        windows = {
            "today": now - timedelta(days=1),
            "last_7_days": now - timedelta(days=7),
            "last_30_days": now - timedelta(days=30),
        }

        result = {}
        for label, since in windows.items():
            qs = Order.objects.filter(created_at__gte=since)
            agg = qs.aggregate(order_count=Count("id"), revenue=Sum("total"))
            result[label] = {
                "order_count": agg["order_count"] or 0,
                "revenue": str(agg["revenue"] or 0),
            }

        # Status breakdown (all time)
        status_counts = {val: Order.objects.filter(status=val).count() for val in Order.Status.values}
        result["by_status"] = status_counts

        return Response(result)


class DashboardTopProductsView(APIView):
    """
    GET /api/admin/dashboard/top-products/?limit=10

    Returns the top-selling products by total revenue (from paid orders).
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.db.models import ExpressionWrapper, F, FloatField

        from shopforge.apps.orders.models import OrderItem

        limit = min(int(request.query_params.get("limit", 10)), 50)
        top = (
            OrderItem.objects.filter(order__payment_status="PAID")
            .values("product_id", "product_name", "product_sku")
            .annotate(
                units_sold=Sum("quantity"),
                total_revenue=Sum(
                    ExpressionWrapper(
                        F("price_at_purchase") * F("quantity"),
                        output_field=FloatField(),
                    )
                ),
            )
            .order_by("-total_revenue")[:limit]
        )
        return Response(list(top))


class DashboardLowStockView(APIView):
    """
    GET /api/admin/dashboard/low-stock/

    Returns products whose available quantity is at or below their reorder level.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.db.models import F

        from shopforge.apps.inventory.models import StockRecord

        records = (
            StockRecord.objects.select_related("product")
            .annotate(available=F("quantity") - F("reserved_quantity"))
            .filter(available__lte=F("reorder_level"))
            .values(
                "product__id",
                "product__name",
                "product__sku",
                "quantity",
                "reserved_quantity",
                "available",
                "reorder_level",
                "reorder_quantity",
            )
        )
        return Response(list(records))


class DashboardRevenueChartView(APIView):
    """
    GET /api/admin/dashboard/revenue-chart/?days=30

    Returns daily revenue for the last N days, suitable for a line chart.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        from shopforge.apps.orders.models import Order

        days = min(int(request.query_params.get("days", 30)), 365)
        since = timezone.now() - timedelta(days=days)

        daily = (
            Order.objects.filter(created_at__gte=since, payment_status="PAID")
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(revenue=Sum("total"), orders=Count("id"))
            .order_by("date")
        )
        return Response(list(daily))
