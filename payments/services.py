import base64
import hashlib
import json
import requests
from django.conf import settings
from rest_framework.exceptions import APIException


class LiqPayAPIError(APIException):
    status_code = 502
    default_detail = "Помилка при зверненні до LiqPay."
    default_code = "liqpay_api_error"


def create_payment(order, return_url: str, result_url: str):
    """
    Створює платіж у LiqPay.
    :param order: Замовлення, яке оплачується
    :param return_url: URL, куди повернеться користувач після оплати
    :param result_url: URL для webhook (куди LiqPay відправить статус)
    """
    # 1. генеруємо унікальний ID для замовлення
    generated_order_id = f"order_{order.id}"

    data = {
        "action": "pay",
        "amount": str(order.total_price),
        "currency": "UAH",
        "description": f"Оплата замовлення #{order.id}",
        "order_id": generated_order_id,
        "version": "3",
        "public_key": settings.LIQPAY_PUBLIC_KEY,
        "sandbox": int(settings.LIQPAY_SANDBOX),  # 1 = тестовий режим
        "result_url": result_url,  # Куди LiqPay відправить webhook
        "server_url": return_url,  # Куди повернеться користувач
    }

    # Формуємо data (base64) та signature
    data_json = json.dumps(data)
    data_base64 = base64.b64encode(data_json.encode("utf-8")).decode("utf-8")

    # Підпис: private_key + data_base64 + private_key
    signature_string = settings.LIQPAY_PRIVATE_KEY + data_base64 + settings.LIQPAY_PRIVATE_KEY
    signature = base64.b64encode(hashlib.sha1(signature_string.encode("utf-8")).digest()).decode("utf-8")

    # Відправляємо запит до LiqPay
    payload = {
        "data": data_base64,
        "signature": signature,
    }

    try:
        response = requests.post(
            "https://www.liqpay.ua/api/3/request",  # <-- це JSON API
            data=payload,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()

        if not result.get("url"):
            print("LIQPAY RAW RESPONSE:", result)
            raise LiqPayAPIError(detail=f"LiqPay не повернув URL. Відповідь API: {result}")

        if result.get("error"):
            raise LiqPayAPIError(detail=result["error"])

        return {
            "payment_id": result.get("payment_id"),
            "liqpay_order_id": result.get("order_id") or generated_order_id,
            "redirect_url": result.get("url"),
        }

    except requests.exceptions.RequestException as e:
        raise LiqPayAPIError(detail=f"Помилка мережі: {str(e)}")


def verify_callback(data_base64: str, signature_base64: str) -> dict:
    """
    Перевіряє підпис від LiqPay у webhook.
    :return: Розпаковані дані або помилка
    """
    # Декодуємо data
    data_json = base64.b64decode(data_base64).decode("utf-8")
    data = json.loads(data_json)

    # Перевіряємо підпис
    expected_signature_string = settings.LIQPAY_PRIVATE_KEY + data_base64 + settings.LIQPAY_PRIVATE_KEY
    expected_signature = base64.b64encode(
        hashlib.sha1(expected_signature_string.encode("utf-8")).digest()
    ).decode("utf-8")

    if expected_signature != signature_base64:
        raise LiqPayAPIError(detail="Невірний підпис від LiqPay")

    return data
