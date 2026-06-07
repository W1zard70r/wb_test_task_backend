import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.cart.models import CartItem
from apps.products.models import Product

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_user_can_add_product_to_cart():
    user = User.objects.create_user(username="buyer", email="buyer@example.com", password="password")
    product = Product.objects.create(title="Bag", description="", price="3000.00", stock_quantity=10)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post("/api/cart/items/", {"product_id": product.id, "quantity": 2}, format="json")

    assert response.status_code == 201
    assert CartItem.objects.get(user=user, product=product).quantity == 2


def test_adding_existing_product_increases_quantity():
    user = User.objects.create_user(username="buyer", email="buyer@example.com", password="password")
    product = Product.objects.create(title="Bag", description="", price="3000.00", stock_quantity=10)
    CartItem.objects.create(user=user, product=product, quantity=2)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post("/api/cart/items/", {"product_id": product.id, "quantity": 3}, format="json")

    assert response.status_code == 201
    assert CartItem.objects.get(user=user, product=product).quantity == 5
