import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException


# Тестові дані на випадок, якщо API НП лежить
MOCK_CITIES = [
    {"Ref": "8d5a980d-391c-11dd-90d9-001a92567626", "Description": "Київ", "Area": "Київська"},
    {"Ref": "db5c88d0-391c-11dd-90d9-001a92567626", "Description": "Львів", "Area": "Львівська"},
]


class NovaPoshtaAPIError(APIException):
    status_code = 502
    default_detail = "Помилка при зверненні до Nova Poshta API"
    default_code = "nova_poshta_api_error"


def get_cities():
    """Отримуємо список міст з Nova Poshta API з кешуванням"""
    cache_key = "nova_poshta_cities"

    # 1. Спроба взяти з кешу
    cities = cache.get(cache_key)
    if cities is not None:
        return cities

    # 2. Якщо в кеші немає, робимо запит до Nova Poshta API
    payload = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": "Address",
        "calledMethod": "getCities",
        "methodProperties": {},
    }

    try:
        response = requests.post(
            "https://api.novaposhta.ua/v2.0/json/",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Перевіряемо, чи повернула Нова Пошта помилку у своєму форматі
        if data.get("success") is False:
            raise NovaPoshtaAPIError(
                detail=data.get("errors", ["Невідома помилка НП"])[0]
            )

        cities = data["data"]

        # 3. Зберігаємо в кеш на 24 години (86400 сек)
        cache.set(cache_key, cities, 86400)

        return cities


    except requests.exceptions.RequestException as e:
        if settings.DEBUG:
            return MOCK_CITIES

        raise NovaPoshtaAPIError(detail=f"Помилка мережі: {str(e)}")


def get_warehouses(city_ref: str):
    """Отримуємо список відділень для конкретного міста за його ref"""
    cache_key = f"nova_poshta_warehouses_{city_ref}"

    warehouses = cache.get(cache_key)
    if warehouses is not None:
        return warehouses

    payload = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "CityRef": city_ref
        },
    }

    try:
        response = requests.post(
            "https://api.novaposhta.ua/v2.0/json/",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("success") is False:
            raise NovaPoshtaAPIError(
                detail=data.get("errors", ["Невідома помилка НП"])[0]
            )

        warehouses = data["data"]

        # Кешуємо відділенн на 12 годин
        cache.set(cache_key, warehouses, 86400)

        return warehouses

    except requests.exceptions.RequestException as e:
        raise NovaPoshtaAPIError(detail=f"Помилка мережі: {str(e)}")


def calculate_delivery_cost(city_recipient_ref: str, weight: float = 1.0):
    """
    Розраховуємо вартість доставки
    :param city_recipient_ref: ref міста-отримувача
    :param weight: вага відправлення в кг (за замовчанням 1 кг)
    """

    cache_key = f"nova_poshta_delivery_cost_{city_recipient_ref}_{weight}"

    # Пробуємо брати з кешу
    cost_data = cache.get(cache_key)
    if cost_data is not None:
        return cost_data

    # Ref Києва як міста відправника (для прикладу)
    CITY_SENDER_REF = "8d5a980d-391c-11dd-90d9-001a92567626"

    payload = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": "InternetDocument",
        "calledMethod": "getDocumentPrice",
        "methodProperties": {
            "CitySender": CITY_SENDER_REF,
            "CityRecipient": city_recipient_ref,
            "Weight": weight,
            "ServiceType": "WarehouseDoors",
            "Cost": "1000" # Оголошена ціна (для прикладу)
        },
    }

    try:
        response = requests.post(
            "https://api.novaposhta.ua/v2.0/json/",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("success") is False:
            raise NovaPoshtaAPIError(detail=data.get("errors", ["Помилка API Nova Poshta"]))

        # API пщвертає список, беремо перший елемент
        result = data["data"][0]

        cost_data = {
            "cost": result.get("Cost", "0.00"), # Вартість доставки
            "estimated_delivery_date": result.get("EstimatedDeliveryDate", "Невідомо"), # Приблизна дата
            "currency": "UAH"
        }

        # КЕшуємо на 12 годин
        cache.set(cache_key, cost_data, 43200)
        return cost_data

    except requests.exceptions.RequestException as e:
        # ПОРЯТУНОК ДЛЯ РОЗРОБКИ
        if settings.DEBUG:
            return {
                "cost": "150.00",
                "estimated_delivery_date": "Завтра",
                "currency": "UAH"
            }
        raise NovaPoshtaAPIError(detail=f"Помилка мережі: {str(e)}")
