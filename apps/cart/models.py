from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from config.settings import base as settings
from apps.products.models import Product


class Cart(models.Model):
    """Кошик користувача. Один користувач = один кошик."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Користувач"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"

    def __str__(self) -> str:
        return f"Кошик {self.user.first_name} {self.user.last_name} - {self.user.email}"

    @property
    def total_price(self) -> Decimal:
        total = sum(
            (item.subtotal for item in self.items.select_related("product").all()),
            Decimal("0.00")
        )
        return total

    @property
    def items_count(self) -> int:
        return sum(item.quantity for item in self.items.select_related("product").all())


class CartItem(models.Model):
    """Позиція в кошику: товар + кількість."""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Кошик"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Кількість"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Позиція кошика"
        verbose_name_plural = "Позиції кошика"
        unique_together = ["cart", "product"]

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.product.price

    def clean(self) -> None:
        if self.quantity > self.product.stock:
            raise ValidationError(f"Cannot add more than {self.product.stock} items to the cart.")
