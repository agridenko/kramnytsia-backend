from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from cart.models import Cart, CartItem
from products.models import Category, Product

User = get_user_model()


class CartModelMixin:
    """Хелпери для створення користувача, товару та кошика."""

    def create_user(self, email="user@example.com", password="pass12345"):
        return User.objects.create_user(
            email=email,
            password=password,
            first_name="Іван",
            last_name="Тестовий",
        )

    def create_product(
        self,
        name="Гра",
        slug="gra",
        price="100.00",
        stock=10,
    ):
        category, _ = Category.objects.get_or_create(
            slug="board-games",
            defaults={"name": "Настільні ігри"},
        )
        return Product.objects.create(
            name=name,
            slug=slug,
            price=Decimal(price),
            stock=stock,
            category=category,
        )

    def create_cart_with_item(self, user=None, product=None, quantity=2):
        user = user or self.create_user()
        product = product or self.create_product()
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
        )
        return cart, item, product, user


class CartModelTests(CartModelMixin, TestCase):
    def test_cart_str(self):
        user = self.create_user()
        cart = Cart.objects.create(user=user)
        self.assertEqual(
            str(cart),
            f"Кошик {user.first_name} {user.last_name} - {user.email}",
        )

    def test_cart_item_str(self):
        cart, item, product, _ = self.create_cart_with_item(quantity=3)
        self.assertEqual(str(item), f"{product.name} x 3")

    def test_cart_item_subtotal(self):
        product = self.create_product(price="49.90")
        cart, item, _, _ = self.create_cart_with_item(
            product=product,
            quantity=3,
        )
        self.assertEqual(item.subtotal, Decimal("149.70"))

    def test_cart_total_price_and_items_count(self):
        user = self.create_user()
        cart = Cart.objects.create(user=user)
        product_a = self.create_product(
            name="Гра A",
            slug="gra-a",
            price="100.00",
            stock=10,
        )
        product_b = self.create_product(
            name="Гра B",
            slug="gra-b",
            price="50.50",
            stock=10,
        )
        CartItem.objects.create(cart=cart, product=product_a, quantity=2)
        CartItem.objects.create(cart=cart, product=product_b, quantity=3)

        self.assertEqual(cart.total_price, Decimal("351.50"))
        self.assertEqual(cart.items_count, 5)

    def test_empty_cart_totals(self):
        user = self.create_user()
        cart = Cart.objects.create(user=user)
        self.assertEqual(cart.total_price, Decimal("0.00"))
        self.assertEqual(cart.items_count, 0)

    def test_cart_item_clean_raises_when_quantity_exceeds_stock(self):
        product = self.create_product(stock=2)
        user = self.create_user()
        cart = Cart.objects.create(user=user)
        item = CartItem(cart=cart, product=product, quantity=5)

        with self.assertRaises(ValidationError) as ctx:
            item.clean()

        self.assertIn("Cannot add more than 2", str(ctx.exception))

    def test_cart_item_unique_together(self):
        cart, _, product, _ = self.create_cart_with_item()
        with self.assertRaises(Exception):
            CartItem.objects.create(cart=cart, product=product, quantity=1)


class CartAPITests(CartModelMixin, APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user()
        self.other_user = self.create_user(email="other@example.com")
        self.product = self.create_product(stock=10, price="120.00")
        self.cart_url = reverse("cart:cart-detail", kwargs={"pk": "me"})
        self.add_item_url = reverse("cart:cart-add-item")
        self.clear_url = reverse("cart:cart-clear")

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_unauthenticated_requests_are_forbidden(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(
            self.add_item_url,
            {"product_id": self.product.id, "quantity": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_creates_empty_cart(self):
        self.authenticate()
        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"], [])
        self.assertEqual(Decimal(response.data["total_price"]), Decimal("0.00"))
        self.assertEqual(response.data["items_count"], 0)
        self.assertTrue(Cart.objects.filter(user=self.user).exists())

    def test_add_item_creates_cart_item(self):
        self.authenticate()
        response = self.client.post(
            self.add_item_url,
            {"product_id": self.product.id, "quantity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 2)
        self.assertEqual(Decimal(response.data["subtotal"]), Decimal("240.00"))
        self.assertEqual(CartItem.objects.filter(cart__user=self.user).count(), 1)

    def test_add_item_increments_existing_quantity(self):
        self.authenticate()
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        response = self.client.post(
            self.add_item_url,
            {"product_id": self.product.id, "quantity": 3},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 4)
        self.assertEqual(CartItem.objects.get(cart=cart).quantity, 4)

    def test_add_item_requires_product_id(self):
        self.authenticate()
        response = self.client.post(
            self.add_item_url,
            {"quantity": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Product ID is required")

    def test_add_item_product_not_found(self):
        self.authenticate()
        response = self.client.post(
            self.add_item_url,
            {"product_id": 99999, "quantity": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Product not found")

    def test_add_item_not_enough_stock(self):
        self.authenticate()
        response = self.client.post(
            self.add_item_url,
            {"product_id": self.product.id, "quantity": 20},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not enough stock", response.data["error"])

    def test_update_item_quantity(self):
        self.authenticate()
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1,
        )
        url = reverse(
            "cart:cart-update-item",
            kwargs={"item_id": item.id},
        )

        response = self.client.post(url, {"quantity": 5}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quantity"], 5)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_update_item_not_found(self):
        self.authenticate()
        url = reverse("cart:cart-update-item", kwargs={"item_id": 99999})

        response = self.client.post(url, {"quantity": 2}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"],
            "Cart item not found in the cart.",
        )

    def test_cannot_update_another_users_cart_item(self):
        other_cart = Cart.objects.create(user=self.other_user)
        other_item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=1,
        )
        self.authenticate(self.user)
        url = reverse(
            "cart:cart-update-item",
            kwargs={"item_id": other_item.id},
        )

        response = self.client.post(url, {"quantity": 9}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_item.refresh_from_db()
        self.assertEqual(other_item.quantity, 1)

    def test_remove_item(self):
        self.authenticate()
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1,
        )
        url = reverse(
            "cart:cart-remove-item",
            kwargs={"item_id": item.id},
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_remove_item_not_found(self):
        self.authenticate()
        url = reverse("cart:cart-remove-item", kwargs={"item_id": 99999})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_clear_cart(self):
        self.authenticate()
        cart = Cart.objects.create(user=self.user)
        second_product = self.create_product(
            name="Інша гра",
            slug="insha-gra",
            price="80.00",
        )
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        CartItem.objects.create(cart=cart, product=second_product, quantity=2)

        response = self.client.post(self.clear_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(cart.items.count(), 0)
        self.assertTrue(Cart.objects.filter(id=cart.id).exists())

    def test_retrieve_returns_items_and_totals(self):
        self.authenticate()
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items_count"], 2)
        self.assertEqual(Decimal(response.data["total_price"]), Decimal("240.00"))
        self.assertEqual(
            Decimal(response.data["items"][0]["subtotal"]),
            Decimal("240.00"),
        )
