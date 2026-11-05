"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf.urls.static import static
from django.conf import settings


admin.site.site_header = "Керування магазином Kramnytsia"
admin.site.site_title = "Панель керування"
admin.site.index_title = "Вітаємо в адміністративній панелі"


urlpatterns = [
    #Адмінка
    path("admin/", admin.site.urls),

    #API товарів
    path(
        "api/v1/",
         include(
             "products.urls",
             namespace="products"
         )
    ),

    #API користувачів
    path(
        "api/v1/users/",
         include(
             "users.urls",
             namespace="users"
         )
    ),

    #API кошик
    path(
        "api/v1/",
         include(
             "cart.urls",
             namespace="cart"
         )
    ),

    #API замовлення
    path(
        "api/v1/",
         include(
             "orders.urls",
             namespace="orders"
         )
    ),

    #API доставки
    path(
        "api/v1/",
         include(
             "delivery.urls",
             namespace="delivery"
         )
    ),

    #Swagger documentations
    path("api/shema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui"
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
