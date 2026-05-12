from django.contrib import admin

from shopforge.apps.coupons.models import Coupon, CouponUsage


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ("order", "user", "discount_applied", "created_at")
    can_delete = False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "uses_count", "max_uses", "is_valid", "valid_until")
    list_filter = ("discount_type", "is_active")
    search_fields = ("code", "description")
    readonly_fields = ("uses_count", "created_at", "updated_at")
    inlines = [CouponUsageInline]
