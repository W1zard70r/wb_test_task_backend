from django.contrib import admin

from apps.products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "stock_quantity", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
