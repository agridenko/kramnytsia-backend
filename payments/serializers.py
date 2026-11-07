from rest_framework import serializers


class CreatePaymentRequestSerializer(serializers.Serializer):
    """Serializer для запиту на створення платежу."""
    order_id = serializers.IntegerField(
        help_text="ID замовлення, яке потрібно оплатити"
    )


class LiqPayCallbackSerializer(serializers.Serializer):
    """Serializer для webhook від LiqPay."""
    data = serializers.CharField(
        help_text="Base64-encoded JSON з даними платежу"
    )
    signature = serializers.CharField(
        help_text="Base64-encoded підпис від LiqPay"
    )
