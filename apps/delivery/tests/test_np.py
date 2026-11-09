import pytest
from unittest.mock import patch
from django.core.cache import cache
from django.test import override_settings

from apps.delivery.services import get_cities
import requests


@pytest.mark.django_db
class TestNovaPoshtaAPI:

    def test_get_cities_caches_response(self):
        # Очищаємо кеш перед тестом для чистоти експерименту
        cache.clear()

        # Мокаємо requests.post, щоб він не робив реальний запит, а повертав фейкові дані
        mock_response_data = {
            "success": True,
            "data": [{"Ref": "test-ref", "Description": "Тестове місто", "Area": "Тестова область"}]
        }

        with patch('delivery.services.requests.post') as mock_post:
            # Налаштовуємо, що має повернути наш мок
            mock_post.return_value.json.return_value = mock_response_data
            mock_post.return_value.raise_for_status.return_value = None

            # Act: Викликаємо функцію двічі
            result1 = get_cities()
            result2 = get_cities()

            # Assert:
            # 1. Результати однакові
            assert result1 == result2
            # 2. Реальний HTTP-запит був зроблений ТІЛЬКИ ОДИН РАЗ (другий раз взято з кешу)
            assert mock_post.call_count == 1

    @override_settings(DEBUG=True)
    def test_get_cities_returns_mock_data_on_api_failure_in_debug(self):
        cache.clear()

        with patch('delivery.services.requests.post') as mock_post:
            # Імітуємо збій мережі
            mock_post.side_effect = requests.exceptions.RequestException("Connection error")

            # Act: викликаємо функцію
            result = get_cities()

            # Assert: перевіряємо, що спрацював "рятувальний круг" (MOCK_CITIES)
            assert len(result) > 0
            assert result[0]["Description"] == "Київ"
