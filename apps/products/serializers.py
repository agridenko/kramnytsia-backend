from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "category",
            "category_name",
            "image",
            "age_from",
            "players_min",
            "players_max",
            "created_at",
            "updated_at",
            "is_available",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )
