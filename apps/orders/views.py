from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.cart.models import Cart
from apps.products.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для обробки замовлень.

    list: Список замовлень поточного користувача
    retrieve: Отримання детальної інформації про замовлення
    checkout: Оформлення замовлення
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product"
        )

    @action(detail=False, methods=["POST"])
    def checkout(self, request):
        """POST /api/orders/checkout/ - оформлення замовлення"""
        try:
            cart = Cart.objects.get(user=self.request.user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = cart.items.select_related("product").all()

        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        delivery_cost = Decimal(request.data.get("delivery_cost", 0))

        # *************************************************************
        # ТРАНЗАКЦІЯ: починаємо оформлення замовлення
        # *************************************************************
        with transaction.atomic():
            # 1. Блакуємо товари для запобігання race condition
            product_ids = [item.product_id for item in cart_items]
            products = Product.objects.select_for_update().filter(id__in=product_ids)
            products_dict = {product.id: product for product in products}

            # 2. Перевіряємо наявність товарів в магазині
            # та рахуємо "total_price" загальну вартість замовлення
            total_price = 0
            order_items_data = []

            for cart_item in cart_items:
                product = products_dict.get(cart_item.product_id)

                if product is None:
                    raise serializers.ValidationError(
                        f"Product {cart_item.product_id} not found"
                    )

                if product.stock < cart_item.quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock for {product.name}. "
                        f"Available: {product.stock}, requested: {cart_item.quantity}"
                    )

                # Фіксуємо ціну на момент замовлення
                item_total = product.price * cart_item.quantity
                total_price += item_total

                order_items_data.append(
                    {
                        "product": product,
                        "quantity": cart_item.quantity,
                        "price": product.price,
                    }
                )

            # 3. Створення замовлення
            order = Order.objects.create(
                user=request.user, total_price=total_price, delivery_cost=delivery_cost
            )

            # 4. Створення елементів замовлення
            order_items = [
                OrderItem(
                    order=order,
                    product=item_data["product"],
                    quantity=item_data["quantity"],
                    price=item_data["price"],
                )
                for item_data in order_items_data
            ]
            OrderItem.objects.bulk_create(order_items)

            # 5. Зменшуємо stock на складі
            for cart_item in cart_items:
                Product.objects.filter(id=cart_item.product_id).update(
                    stock=F("stock") - cart_item.quantity
                )

            # 6. Очищаємо кошик
            cart.delete()

            # -------------------------------------------------------------------
            # ТРАНЗАКЦІЯ: успішно завершена
            # -------------------------------------------------------------------
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """POST /api/orders/{pk}/cancel/ - скасувати замовлення"""
        order = self.get_object()

        if order.status != Order.Status.NEW:
            return Response(
                {"error": "Can only cancel NEW orders"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # повертаємо товари на склад
            for item in order.items.all():
                Product.objects.filter(id=item.product_id).update(
                    stock=F("stock") + item.quantity
                )

            order.status = Order.Status.CANCELED
            order.save()

        serializers = self.get_serializer(order)
        return Response(serializers.data)
