from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product


class CartViewSet(viewsets.GenericViewSet):
    """
    API cart viewset

    retrieve: Отримати кошик поточного користувача
    add_item: Додати товар до кошика
    update_item: Оновити кількість товару в кошику
    remove_item: Видалити товар з кошика
    clear: Очистити кошик
    """

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Повертає кошик поточного користувача"""
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        """Отримуемо або створюэмо кошик поточного користувача"""
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def retrieve(self, request, *args, **kwargs):
        """GET api/cart/ отримати кошик поточного користувача"""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """POST api/cart/add_item додати товар до кошика"""
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)


        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)

            if product.stock < quantity:
                return Response(
                    {"error": f"Not enough stock. Available: {product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = self.get_object()

        #Перевірка чи існує товар в кошику
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            #якщо товар вже є в кошику, то збільшуємо його кількість
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["post"],
        url_path="update_item/(?P<item_id>[0-9]+)"
    )
    def update_item(self, request, item_id):
        """POST api/cart/update_item/(?P<item_id>[0-9]+) оновити кількість товару в кошику"""
        quantity = request.data.get("quantity", 1)

        cart = self.get_object()

        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found in the cart."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="remove_item/(?P<item_id>[0-9]+)"
    )
    def remove_item(self, request, item_id):
        """POST api/cart/remove_item/(?P<item_id>[0-9]+) видалити товар з кошику"""
        cart = self.get_object()

        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found in the cart."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        return Response(
            {"message": "Cart item removed successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=["post"]
    )
    def clear(self, request):
        """POST api/cart/clear очистити кошик"""
        cart = self.get_object()
        cart.items.all().delete()
        return Response(
            {"message": "Cart cleared successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
