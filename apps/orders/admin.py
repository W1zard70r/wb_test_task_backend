from django.contrib import admin

from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_title_snapshot", "price_snapshot", "quantity", "total_price")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    list_select_related = ("user",)
    search_fields = ("user__username", "user__email", "items__product_title_snapshot")
    readonly_fields = ("user", "status", "total_amount", "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product_title_snapshot", "quantity", "price_snapshot", "total_price")
    list_filter = ("order__created_at",)
    list_select_related = ("order", "product")
    search_fields = ("product_title_snapshot", "order__user__username", "order__user__email")
    readonly_fields = ("order", "product", "product_title_snapshot", "price_snapshot", "quantity", "total_price")
