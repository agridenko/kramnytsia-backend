from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .models import Category, Product
from .permissions import IsAdminOrContentManagerOrReadOnly
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrContentManagerOrReadOnly]

    """Кешуемо на 24 години"""

    def list(self, request, *args, **kwargs):
        cache_key = "category_list"

        # 1. Пробуэмо дыстати з кешу
        cache_data = cache.get(cache_key)
        if cache_data is not None:
            return Response(cache_data)

        # 2. Якщо немає — виконуємо стандартний запит до БД
        response = super().list(request, *args, **kwargs)

        # 3. Зберігаємо результат у кеш на 24 години (86400 сек)
        cache.set(cache_key, response.data, 60 * 60 * 24)
        return response


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrContentManagerOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "age_from", "players_min", "players_max", "price"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]

    """кешування списку продуктів на 1 годину"""

    def list(self, request, *args, **kwargs):
        cache_key = "products_list"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)

        # Кешуємо на 1 годину (3600 сек)
        cache.set(cache_key, response.data, timeout=60 * 60)
        return response
