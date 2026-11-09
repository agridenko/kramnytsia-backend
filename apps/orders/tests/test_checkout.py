import pytest
from rest_framework.test import APIClient
from rest_framework import status

from apps.products.factories import ProductFactory
from apps.orders.models import Order
from apps.cart.models import Cart, CartItem
from django.contrib.auth import get_user_model


@pytest.fixture
def api_client():
    """Фікстура: створює API-клієнт для тестів."""
    return APIClient()


@pytest.fixture
def user(db):
    """Фікстура: створює тестового користувача."""
    User = get_user_model()
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Фікстура: API-клієнт з авторизованим користувачем."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def product_with_stock(db):
    """Фікстура: товар з 10 одиницями на складі."""
    return ProductFactory(stock=10, price="1000.00")


@pytest.mark.django_db
class TestCheckout:
    """Тести для ендпоінта оформлення замовлення."""

    def test_checkout_successfully_creates_order(
            self, authenticated_client, user, product_with_stock
    ):
        """Успішне оформлення замовлення має зменшити stock."""
        # Arrange: додаємо товар у кошик
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product_with_stock, quantity=3)

        # Act: оформлюємо замовлення
        response = authenticated_client.post("/api/v1/orders/checkout/")

        # Assert: перевіряємо результат
        assert response.status_code == status.HTTP_201_CREATED

        # Перевіряємо, що замовлення створено
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.user == user
        assert order.total_price == 3000  # 1000 * 3

        # Перевіряємо, що stock зменшився
        product_with_stock.refresh_from_db()
        assert product_with_stock.stock == 7  # 10 - 3

        # Перевіряємо, що кошик очищено
        assert cart.items.count() == 0

    def test_checkout_fails_when_cart_is_empty(
            self, authenticated_client, user
    ):
        """Оформлення з порожнім кошиком має повернути 400."""
        Cart.objects.create(user=user)  # порожній кошик

        response = authenticated_client.post("/api/v1/orders/checkout/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty" in response.data["error"].lower()
        assert Order.objects.count() == 0

    def test_checkout_fails_when_not_enough_stock(
            self, authenticated_client, user, product_with_stock
    ):
        """Не можна купити більше, ніж є на складі."""
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product_with_stock, quantity=100)  # просимо 100, є 10

        response = authenticated_client.post("/api/v1/orders/checkout/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Order.objects.count() == 0

        # Stock має залишитися незмінним (транзакція відкотилася)
        product_with_stock.refresh_from_db()
        assert product_with_stock.stock == 10

    def test_checkout_requires_authentication(
            self, api_client, product_with_stock
    ):
        """Без авторизації оформити замовлення не можна."""
        response = api_client.post("/api/v1/orders/checkout/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED