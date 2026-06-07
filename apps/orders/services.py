import logging

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.cart.models import CartItem
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from common.exceptions import ConflictError

logger = logging.getLogger("orders")
User = get_user_model()


@transaction.atomic
def create_order_from_cart(user, cart_item_ids=None):
    queryset = (
        CartItem.objects.select_related("product")
        .select_for_update()
        .filter(user=user)
        .order_by("id")
    )
    if cart_item_ids is not None:
        queryset = queryset.filter(id__in=cart_item_ids)

    cart_items = list(queryset)
    if cart_item_ids is not None:
        found_ids = {item.id for item in cart_items}
        missing_ids = set(cart_item_ids) - found_ids
        if missing_ids:
            raise ConflictError("Some cart items were not found.", code="cart_items_not_found")

    if not cart_items:
        raise ConflictError("Cart is empty.", code="empty_cart")

    product_ids = [item.product_id for item in cart_items]
    products = {
        product.id: product
        for product in Product.objects.select_for_update().filter(id__in=product_ids)
    }

    total_amount = 0
    for item in cart_items:
        product = products[item.product_id]
        if not product.is_active:
            raise ConflictError(f"Product '{product.title}' is not available.", code="inactive_product")
        if product.stock_quantity < item.quantity:
            raise ConflictError(f"Not enough stock for '{product.title}'.", code="insufficient_stock")
        total_amount += product.price * item.quantity

    locked_user = User.objects.select_for_update().get(pk=user.pk)
    if locked_user.balance < total_amount:
        raise ConflictError("Insufficient balance.", code="insufficient_balance")

    locked_user.balance -= total_amount
    locked_user.save(update_fields=["balance"])

    order = Order.objects.create(user=locked_user, total_amount=total_amount)
    order_items = []
    for item in cart_items:
        product = products[item.product_id]
        product.stock_quantity -= item.quantity
        product.save(update_fields=["stock_quantity", "updated_at"])
        order_items.append(
            OrderItem(
                order=order,
                product=product,
                product_title_snapshot=product.title,
                price_snapshot=product.price,
                quantity=item.quantity,
                total_price=product.price * item.quantity,
            )
        )
    OrderItem.objects.bulk_create(order_items)
    CartItem.objects.filter(id__in=[item.id for item in cart_items]).delete()

    logger.info(
        "Order created successfully: order_id=%s user_id=%s total=%s items=%s",
        order.id,
        locked_user.id,
        total_amount,
        len(order_items),
    )
    return order
