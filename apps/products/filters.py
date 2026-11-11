import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    # Вказуємо, що фільтр 'category' має шукати
    # за полем 'slug' пов'язаної моделі Category
    category = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="iexact"
    )

    # Також залишаємо можливість фільтрувати за наявністю (stock)
    stock = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")

    class Meta:
        model = Product
        fields = ["category", "stock"]
