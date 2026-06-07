from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_user_can_register():
    client = APIClient()

    response = client.post(
        "/api/auth/register/",
        {
            "username": "alice",
            "email": "alice@example.com",
            "password": "strong-password",
        },
        format="json",
    )

    assert response.status_code == 201
    assert User.objects.filter(username="alice").exists()
    assert "password" not in response.data


def test_authenticated_user_can_top_up_balance():
    user = User.objects.create_user(username="bob", email="bob@example.com", password="password")
    client = APIClient()
    client.force_authenticate(user)

    response = client.post("/api/auth/me/balance/top-up/", {"amount": "150.50"}, format="json")

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.balance == Decimal("150.50")
