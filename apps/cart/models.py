from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.products.models import Product


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_cart_product_per_user"),
        ]
        ordering = ["created_at"]

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return f"{self.user_id}: {self.product_id} x {self.quantity}"
