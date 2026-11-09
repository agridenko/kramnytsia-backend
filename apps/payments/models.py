from django.db import models
from apps.orders.models import Order


class Payment(models.Model):
    """Платіж через платіжну систему LiqPay"""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Очікує оплати"
        SUCCESS = "SUCCESS", "Оплачено"
        FAILURE = "FAILURE", "Помилка оплати"
        EXPIRED = "EXPIRED", "Прострочено"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name="Замовлення",
    )
    liqpay_order_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="LiqPay Order ID",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сума",
    )
    currency = models.CharField(
        max_length=3,
        default="UAH",
        verbose_name="Валюта",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    response_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Дані відповіді LiqPay",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Платіж #{self.id} для замовлення #{self.order.id}"
