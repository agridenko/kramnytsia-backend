from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.orders.tasks import send_order_confirmation_email
from apps.users.throttles import PaymentRateThrottle

from .models import Payment
from .serializers import CreatePaymentRequestSerializer, LiqPayCallbackSerializer
from .services import create_payment, verify_callback


class CreatePaymentView(APIView):
    """POST /api/payments/create/ - Створити платіж для замовлення"""

    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    @extend_schema(
        request=CreatePaymentRequestSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "payment_id": {"type": "string"},
                    "redirect_url": {"type": "string"},
                },
            },
            400: {"type": "object"},
            404: {"type": "object"},
            502: {"type": "object"},
        },
        description="Створює платіж через LiqPay для вказаного замовлення. "
        "Повертає URL для переходу до оплати.",
    )
    def post(self, request):
        serializer = CreatePaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Замовлення не знайдено"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status != Order.Status.NEW:
            return Response(
                {"error": "Можна оплатити тільки нове замовлення"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Перевіряємо, чи вже є платіж для цього замовлення
        if hasattr(order, "payment"):
            return Response(
                {
                    "payment_id": order.payment.liqpay_order_id,
                    "redirect_url": f"https://www.liqpay.ua/checkout"
                    f"?order_id={order.payment.liqpay_order_id}",
                },
                status=status.HTTP_200_OK,
            )

        # Створюємо платіж
        try:
            payment_data = create_payment(
                order=order,
                # Для локальної розробки
                return_url="http://127.0.0.1:8000/api/payments/result/",
                # Webhook
                result_url="http://127.0.0.1:8000/api/payments/callback/",
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Зберігаємо платіж у БД
        with transaction.atomic():
            # Додаємо захисну перевірку: якщо чомусь все
            # одно прийшов None, використовуємо ID замовлення
            safe_liqpay_order_id = (
                payment_data.get("liqpay_order_id") or f"order_{order.id}"
            )

            payment = Payment.objects.create(
                order=order,
                liqpay_order_id=safe_liqpay_order_id,
                amount=order.total_price,
                currency="UAH",
                status=Payment.Status.PENDING,
            )

        return Response(
            {
                "payment_id": payment.liqpay_order_id,
                "redirect_url": payment_data.get("redirect_url"),
            },
            status=status.HTTP_201_CREATED,
        )


class LiqPayCallbackView(APIView):
    """POST /api/payments/callback/ - Webhook від LiqPay"""

    permission_classes = []  # LiqPay відправляє без авторизації

    @extend_schema(
        request=LiqPayCallbackSerializer,
        responses={
            200: {"type": "object"},
            400: {"type": "object"},
            404: {"type": "object"},
        },
        description="Webhook від LiqPay для оновлення статусу платежу. "
        "Використовується для імітації оплати в локальній розробці.",
    )
    def post(self, request):
        data_base64 = request.data.get("data")
        signature_base64 = request.data.get("signature")

        if not data_base64 or not signature_base64:
            return Response(
                {"error": "Відсутні дані або підпис"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = verify_callback(data_base64, signature_base64)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Оновлюємо статус платежу
        order_id = data.get("order_id")
        payment_status = data.get("status")

        try:
            payment = Payment.objects.get(liqpay_order_id=order_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Платіж не знайдено"},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            if payment_status == "success":
                payment.status = Payment.Status.SUCCESS
                payment.order.status = Order.Status.PAID

                # Викликаємо фонову задачу для відправки email підтвердження
                send_order_confirmation_email.delay(payment.order.id)

            elif payment_status in ["error", "failure"]:
                payment.status = Payment.Status.FAILURE
            elif payment_status == "wait_accept":
                payment.status = Payment.Status.PENDING

            payment.response_data = data
            payment.save()
            payment.order.save()

        return Response({"success": True})


class LiqPayResultView(APIView):
    """GET /api/payments/result/ - Куди повертається користувач після оплати"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Тут можна показати сторінку "Дякуємо за оплату!"
        return Response({"message": "Дякуємо за оплату!"})
