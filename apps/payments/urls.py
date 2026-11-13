from django.urls import path

from .views import CreatePaymentView, LiqPayCallbackView, LiqPayResultView

urlpatterns = [
    path("payments/create/", CreatePaymentView.as_view(), name="create-payment"),
    path("payments/callback/", LiqPayCallbackView.as_view(), name="liqpay-callback"),
    path("payments/result/", LiqPayResultView.as_view(), name="liqpay-result"),
]

app_name = "payments"
