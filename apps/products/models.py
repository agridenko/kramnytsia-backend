import datetime
import pathlib
import uuid

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Категорія товарів (категорія, в якій розміщуються товари)"""

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Назва категорії",
        help_text="Наприклад: 'Смартфони', 'Ноутбуки', 'Планшети'",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="URL-адреса категорії",
        help_text="URL-адреса для доступу до категорії товарів",
    )

    class Meta:
        verbose_name = "Категорія товарів"
        verbose_name_plural = "Категорії товарів"

    def __str__(self):
        return self.name


def product_image_path(instance: "Product", filename: str) -> pathlib.Path:
    filename = (
        f"{slugify(instance.slug)}_{uuid.uuid4()}" + pathlib.Path(filename).suffix
    )
    date_path = datetime.datetime.now().strftime("%Y/%m/%d/")
    return pathlib.Path(f"uploads/products/{date_path}") / pathlib.Path(filename)


class Product(models.Model):
    """Товар (інформація про товар)"""

    name = models.CharField(max_length=255, verbose_name="Назва товару")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="URL-адреса товару",
        help_text="URL-адреса для доступу до товару",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Опис товару",
        help_text="Опис товару, який буде відображатися на сторінці товару",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Ціна товару"
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Залишок на складі",
        help_text="Кількість товарів на складі",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категорія товару",
    )
    image = models.ImageField(
        upload_to=product_image_path,
        blank=True,
        verbose_name="Зображення",
    )
    age_from = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Вік від",
        help_text="Мінімальний вік гравця",
    )
    players_min = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Мінімальна кількість гравців",
        help_text="Мінімальна кількість гравців, необхідна для гри",
    )
    players_max = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Максимальна кількість гравців",
        help_text="Максимальна кількість гравців, необхідна для гри",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ["-created_at"]

    @property
    def is_available(self) -> bool:
        return self.stock > 0

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("product_detail", args=[self.slug])
