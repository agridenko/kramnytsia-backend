from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import calculate_delivery_cost, get_cities, get_warehouses


class NovaPoshtaCitiesViewset(APIView):
    """GET /api/delivery/np/cities/ - Отримуємо список міст для Нова Пошта"""

    permission_classes = [AllowAny]

    def get(self, request):
        cities = get_cities()
        # Відфільтровуємо зайві поля
        filtered_cities = [
            {
                "ref": city["Ref"],
                "name": city["Description"],
                "area": city.get("Area", ""),
            }
            for city in cities
        ]

        return Response(filtered_cities)


class NovaPoshtaWarehousesViewset(APIView):
    """GET /api/delivery/np/warehouses/?city_ref=xxx - Спсиок відділень міста"""

    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="city_ref",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Ref міста (отримати з ендпоінта /cities/)",
                required=True,
            )
        ]
    )
    def get(self, request):
        city_ref = request.query_params.get("city_ref")
        if not city_ref:
            return Response({"error": "City ref is required"}, status=400)

        warehouses = get_warehouses(city_ref)

        filtered_warehouses = [
            {
                "ref": warehouse["Ref"],
                "name": warehouse["Description"],
                "address": warehouse.get("Address", ""),
            }
            for warehouse in warehouses
        ]

        return Response(filtered_warehouses)


class NovaPoshtaDeliveryCostView(APIView):
    """GET /api/delivery/np/cost/ - Стоимість доставки"""

    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="city_ref",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Ref міста отримувача",
                required=True,
            ),
            OpenApiParameter(
                name="weight",
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description="Вага посилки в кг (за замовчанням 1 кг)",
                required=True,
            ),
        ]
    )
    def get(self, request):
        city_ref = request.query_params.get("city_ref")
        weight = request.query_params.get("weight", 1.0)

        if not city_ref:
            return Response({"error": "Параметр city_ref є обов'язковим"}, status=400)

        try:
            weight = float(weight)
        except ValueError:
            return Response(
                {"error": "Параметр weight повинен бути числом"}, status=400
            )

        cost_data = calculate_delivery_cost(city_ref, weight)
        return Response(cost_data)
