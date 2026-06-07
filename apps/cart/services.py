from django.db import transaction

from apps.cart.models import CartItem


def get_user_cart_items(user):
    return CartItem.objects.select_related("product").filter(user=user)


def get_cart_payload(user):
    items = get_user_cart_items(user)
    total = sum((item.total_price for item in items), start=0)
    return {"items": items, "total_price": total}


@transaction.atomic
def add_item_to_cart(*, user, product, quantity):
    item, created = CartItem.objects.select_for_update().get_or_create(
        user=user,
        product=product,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity
        item.save(update_fields=["quantity", "updated_at"])
    return item


def update_cart_item_quantity(*, item, quantity):
    item.quantity = quantity
    item.save(update_fields=["quantity", "updated_at"])
    return item


def clear_cart(user):
    return CartItem.objects.filter(user=user).delete()
