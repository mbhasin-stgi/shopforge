from django.contrib import admin

from shopforge.apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "author", "rating", "is_verified_purchase", "is_approved", "created_at")
    list_filter = ("rating", "is_verified_purchase", "is_approved")
    search_fields = ("product__name", "author__email", "title")
    readonly_fields = ("created_at", "updated_at")
    actions = ["approve_reviews", "hide_reviews"]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Hide selected reviews")
    def hide_reviews(self, request, queryset):
        queryset.update(is_approved=False)
