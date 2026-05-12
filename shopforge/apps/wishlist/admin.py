from django.contrib import admin

from shopforge.apps.wishlist.models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("owner", "created_at")
    search_fields = ("owner__email",)
    inlines = [WishlistItemInline]
