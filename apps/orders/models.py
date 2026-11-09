from django.db import models

from config.settings import base as settings
from apps.products.models import Product
from decimal import Decimal


class Order(models.Model):
    """Замовлення користувача"""

    class Status(models.TextChoices):
        NEW = "NEW", "Нове"
        PAID = "PAID", "Оплачено"
        SHIPPED = "SHIPPED", "Відправлено"
        DELIVERED = "DELIVERED", "Доставлено"
        CANCELED = "CANCELED", "Скасовано"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Користувач"
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Загальна вартість"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Замовлення #{self.id} від {self.user.first_name} {self.user.last_name} - {self.user.email}"


class OrderItem(models.Model):
    """Позиція замовлення"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Замовлення"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(verbose_name="Кількість")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна на момент замовлення"
    )

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.price
