from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "subtotal",
            "added_at"
        ]
        read_only_fields = ["added_at"]


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "total_price",
            "items_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
