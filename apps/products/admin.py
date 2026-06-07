from django.contrib import admin

from apps.products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "stock_quantity", "is_active", "updated_at")
    list_display_links = ("id", "title")
    list_editable = ("price", "stock_quantity", "is_active")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("title", "description")
    ordering = ("title",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "description", "is_active")}),
        ("Pricing and stock", {"fields": ("price", "stock_quantity")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
