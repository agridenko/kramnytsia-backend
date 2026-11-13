import base64
import hashlib
import json

from rest_framework.exceptions import APIException

from config.settings import base as settings


class LiqPayAPIError(APIException):
    status_code = 502
    default_detail = "Помилка при зверненні до LiqPay."
    default_code = "liqpay_api_error"


def create_payment(order, return_url: str, server_url: str):
    """
    Генерує дані для form-based checkout LiqPay.
    НЕ робить HTTP-запитів — просто формує data + signature.

    :param order: Замовлення, яке оплачується
    :param return_url: URL, куди повернеться КОРИСТУВАЧ після оплати (браузер)
    :param server_url: URL, куди LiqPay відправить WEBHOOK (сервер, POST)
    """
    generated_order_id = f"order_{order.id}"

    # result_url = повернення користувача (браузер)
    # server_url = webhook (сервер)
    data = {
        "action": "pay",
        "amount": str(order.total_with_delivery),  # З урахуванням доставки!
        "currency": "UAH",
        "description": f"Оплата замовлення #{order.id} у Kramnytsia",
        "order_id": generated_order_id,
        "version": "3",
        "public_key": settings.LIQPAY_PUBLIC_KEY.strip(),
        "sandbox": int(settings.LIQPAY_SANDBOX),
        "result_url": return_url,  # ✅ Куди повернеться користувач
        "server_url": server_url,  # ✅ Куди прийде webhook
    }

    # Формуємо base64 data
    data_json = json.dumps(data, separators=(",", ":"))
    data_base64 = base64.b64encode(data_json.encode("utf-8")).decode("utf-8")

    # Підпис: private_key + data_base64 + private_key
    private_key = settings.LIQPAY_PRIVATE_KEY.strip()
    signature_string = private_key + data_base64 + private_key
    signature = base64.b64encode(
        hashlib.sha1(signature_string.encode("utf-8")).digest()
    ).decode("utf-8")

    return {
        "liqpay_order_id": generated_order_id,
        "data": data_base64,
        "signature": signature,
        "checkout_url": "https://www.liqpay.ua/api/3/checkout",
    }


def verify_callback(data_base64: str, signature_base64: str) -> dict:
    """Перевіряє підпис від LiqPay у webhook."""
    data_json = base64.b64decode(data_base64).decode("utf-8")
    data = json.loads(data_json)

    expected_signature_string = (
        settings.LIQPAY_PRIVATE_KEY.strip()
        + data_base64
        + settings.LIQPAY_PRIVATE_KEY.strip()
    )
    expected_signature = base64.b64encode(
        hashlib.sha1(expected_signature_string.encode("utf-8")).digest()
    ).decode("utf-8")

    if expected_signature != signature_base64:
        raise LiqPayAPIError(detail="Невірний підпис від LiqPay")

    return data
