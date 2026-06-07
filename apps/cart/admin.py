from django.contrib import admin

from apps.cart.models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity", "total_price", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    list_select_related = ("user", "product")
    search_fields = ("user__username", "user__email", "product__title")
    readonly_fields = ("total_price", "created_at", "updated_at")
