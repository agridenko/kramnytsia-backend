import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from products.factories import ProductFactory
from cart.models import Cart, CartItem


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(email="cart_test@example.com", password="testpass123")


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def product(db):
    return ProductFactory(stock=10, price="500.00")


@pytest.mark.django_db
class TestCartAPI:

    def test_add_item_creates_cart_item(self, auth_client, user, product):
        # Arrange: Кошик порожній
        assert CartItem.objects.count() == 0

        # Act: Додаємо товар
        response = auth_client.post("/api/v1/cart/add_item/", {"product_id": product.id, "quantity": 2})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert CartItem.objects.count() == 1
        cart_item = CartItem.objects.first()
        assert cart_item.quantity == 2
        assert cart_item.product == product

    def test_add_item_increments_existing_quantity(self, auth_client, user, product):
        # Arrange: Додаємо товар перший раз
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=2)

        # Act: Додаємо той самий товар ще раз
        response = auth_client.post("/api/v1/cart/add_item/", {"product_id": product.id, "quantity": 3})

        # Assert: Кількість має збільшитись (2 + 3 = 5), а новий запис не створюється
        assert response.status_code == status.HTTP_201_CREATED
        assert CartItem.objects.count() == 1
        cart_item = CartItem.objects.first()
        cart_item.refresh_from_db()  # Оновлюємо з БД
        assert cart_item.quantity == 5

    def test_remove_item(self, auth_client, user, product):
        # Arrange
        cart = Cart.objects.create(user=user)
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)

        # Act: Видаляємо за ID
        response = auth_client.post(f"/api/v1/cart/remove_item/{cart_item.id}/")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CartItem.objects.count() == 0

    def test_clear_cart(self, auth_client, user, product):
        # Arrange: Додаємо 2 різні товари
        product2 = ProductFactory(stock=5, price="300.00")
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        CartItem.objects.create(cart=cart, product=product2, quantity=1)

        # Act: Очищаємо кошик
        response = auth_client.post("/api/v1/cart/clear/")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CartItem.objects.count() == 0
