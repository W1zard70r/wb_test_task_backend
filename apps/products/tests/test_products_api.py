import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.products.models import Product

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_products_are_publicly_readable():
    Product.objects.create(title="Keyboard", description="Mechanical", price="2500.00", stock_quantity=5)
    client = APIClient()

    response = client.get("/api/products/")

    assert response.status_code == 200
    assert response.data["count"] == 1


def test_regular_user_cannot_create_product():
    user = User.objects.create_user(username="user", email="user@example.com", password="password")
    client = APIClient()
    client.force_authenticate(user)

    response = client.post(
        "/api/products/",
        {"title": "Mouse", "description": "", "price": "1000.00", "stock_quantity": 3},
        format="json",
    )

    assert response.status_code == 403


def test_staff_user_can_create_product():
    user = User.objects.create_user(username="admin", email="admin@example.com", password="password", is_staff=True)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post(
        "/api/products/",
        {"title": "Mouse", "description": "", "price": "1000.00", "stock_quantity": 3},
        format="json",
    )

    assert response.status_code == 201
    assert Product.objects.filter(title="Mouse").exists()
