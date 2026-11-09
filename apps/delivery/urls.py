from django.urls import path
from .views import NovaPoshtaCitiesViewset, NovaPoshtaWarehousesViewset, NovaPoshtaDeliveryCostView

urlpatterns = [
    path("delivery/np/cities/", NovaPoshtaCitiesViewset.as_view(), name="np_cities"),
    path("delivery/np/warehouses/", NovaPoshtaWarehousesViewset.as_view(), name="np_warehouses"),
    path("delivery/np/cost/", NovaPoshtaDeliveryCostView.as_view(), name="np_delivery_cost"),
]

app_name = "delivery"
