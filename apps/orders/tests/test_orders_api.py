from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.cart.models import CartItem
from apps.orders.models import Order
from apps.products.models import Product

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_create_order_from_cart_charges_balance_decreases_stock_and_clears_cart():
    user = User.objects.create_user(
        username="buyer",
        email="buyer@example.com",
        password="password",
        balance=Decimal("1000.00"),
    )
    product = Product.objects.create(title="Book", description="", price=Decimal("100.00"), stock_quantity=5)
    CartItem.objects.create(user=user, product=product, quantity=2)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post("/api/orders/", {}, format="json")

    user.refresh_from_db()
    product.refresh_from_db()
    assert response.status_code == 201
    assert user.balance == Decimal("800.00")
    assert product.stock_quantity == 3
    assert CartItem.objects.filter(user=user).count() == 0
    order = Order.objects.get(user=user)
    assert order.total_amount == Decimal("200.00")
    assert order.items.get().product_title_snapshot == "Book"


def test_order_is_not_created_when_balance_is_insufficient_and_state_is_unchanged():
    user = User.objects.create_user(
        username="buyer",
        email="buyer@example.com",
        password="password",
        balance=Decimal("50.00"),
    )
    product = Product.objects.create(title="Book", description="", price=Decimal("100.00"), stock_quantity=5)
    CartItem.objects.create(user=user, product=product, quantity=2)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post("/api/orders/", {}, format="json")

    user.refresh_from_db()
    product.refresh_from_db()
    assert response.status_code == 409
    assert user.balance == Decimal("50.00")
    assert product.stock_quantity == 5
    assert CartItem.objects.filter(user=user).count() == 1
    assert Order.objects.count() == 0


def test_order_is_not_created_when_stock_is_insufficient_and_balance_is_unchanged():
    user = User.objects.create_user(
        username="buyer",
        email="buyer@example.com",
        password="password",
        balance=Decimal("1000.00"),
    )
    product = Product.objects.create(title="Book", description="", price=Decimal("100.00"), stock_quantity=1)
    CartItem.objects.create(user=user, product=product, quantity=2)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post("/api/orders/", {}, format="json")

    user.refresh_from_db()
    product.refresh_from_db()
    assert response.status_code == 409
    assert user.balance == Decimal("1000.00")
    assert product.stock_quantity == 1
    assert CartItem.objects.filter(user=user).count() == 1
    assert Order.objects.count() == 0


def test_create_order_from_selected_cart_items_leaves_unselected_items_in_cart():
    user = User.objects.create_user(
        username="buyer",
        email="buyer@example.com",
        password="password",
        balance=Decimal("1000.00"),
    )
    selected_product = Product.objects.create(
        title="Selected book",
        description="",
        price=Decimal("100.00"),
        stock_quantity=5,
    )
    skipped_product = Product.objects.create(
        title="Skipped book",
        description="",
        price=Decimal("300.00"),
        stock_quantity=5,
    )
    selected_item = CartItem.objects.create(user=user, product=selected_product, quantity=2)
    skipped_item = CartItem.objects.create(user=user, product=skipped_product, quantity=1)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post("/api/orders/", {"cart_item_ids": [selected_item.id]}, format="json")

    user.refresh_from_db()
    selected_product.refresh_from_db()
    skipped_product.refresh_from_db()
    assert response.status_code == 201
    assert user.balance == Decimal("800.00")
    assert selected_product.stock_quantity == 3
    assert skipped_product.stock_quantity == 5
    assert CartItem.objects.filter(id=selected_item.id).exists() is False
    assert CartItem.objects.filter(id=skipped_item.id).exists() is True
    order = Order.objects.get(user=user)
    assert order.total_amount == Decimal("200.00")
    assert order.items.count() == 1
    assert order.items.get().product_title_snapshot == "Selected book"


def test_create_order_rejects_cart_items_from_another_user():
    user = User.objects.create_user(
        username="buyer",
        email="buyer@example.com",
        password="password",
        balance=Decimal("1000.00"),
    )
    other_user = User.objects.create_user(
        username="other",
        email="other@example.com",
        password="password",
        balance=Decimal("1000.00"),
    )
    product = Product.objects.create(title="Book", description="", price=Decimal("100.00"), stock_quantity=5)
    other_item = CartItem.objects.create(user=other_user, product=product, quantity=1)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post("/api/orders/", {"cart_item_ids": [other_item.id]}, format="json")

    assert response.status_code == 409
    assert Order.objects.count() == 0
    assert CartItem.objects.filter(id=other_item.id).exists() is True
