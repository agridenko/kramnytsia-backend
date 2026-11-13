from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.orders.tasks import send_order_confirmation_email
from apps.users.throttles import PaymentRateThrottle
from config.settings import base as settings

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

        # Якщо платіж вже існує — повертаємо його дані
        if hasattr(order, "payment"):
            payment = order.payment
            # Регенеруємо data/signature (вони можуть протухнути)
            payment_data = create_payment(
                order=order,
                return_url=f"{settings.FRONTEND_URL}/payment/success",
                server_url=f"{settings.BACKEND_URL}/api/v1/payments/callback/",
            )
            return Response(
                {
                    "payment_id": payment.liqpay_order_id,
                    **payment_data,
                },
                status=status.HTTP_200_OK,
            )

        # return_url = куди повернеться КОРИСТУВАЧ (FRONT-END React-сторінка)
        # server_url = куди прийде WEBHOOK (бекенд)
        try:
            payment_data = create_payment(
                order=order,
                return_url=f"{settings.FRONTEND_URL}/payment/success",
                server_url=f"{settings.BACKEND_URL}/api/v1/payments/callback/",
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        with transaction.atomic():
            payment = Payment.objects.create(
                order=order,
                liqpay_order_id=payment_data["liqpay_order_id"],
                amount=order.total_with_delivery,  # З доставкою
                currency="UAH",
                status=Payment.Status.PENDING,
            )

        return Response(payment_data, status=status.HTTP_201_CREATED)


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
            print(f"LIQPAY VERIFY ERROR: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Оновлюємо статус платежу
        order_id = data.get("order_id")
        payment_status = data.get("status")

        print(
            f"🔔 LIQPAY WEBHOOK RECEIVED: order_id={order_id}, status={payment_status}"
        )

        try:
            # LiqPay іноді передає order_id як "order_1", а іноді просто "1"
            # Спробуємо знайти за повним ID, а якщо не вийде - за числом
            payment = Payment.objects.get(liqpay_order_id=order_id)
        except Payment.DoesNotExist:
            # Фолбек: якщо order_id прийшов як число, шукаємо за order_id замовлення
            try:
                clean_order_id = str(order_id).replace("order_", "")
                payment = Payment.objects.get(order_id=clean_order_id)
            except Payment.DoesNotExist:
                print(f"⚠️ PAYMENT NOT FOUND for order_id: {order_id}")
                return Response(
                    {"error": "Платіж не знайдено"}, status=status.HTTP_404_NOT_FOUND
                )

        with transaction.atomic():
            # 🔥 ДОДАНО "sandbox" до успішних статусів!
            if payment_status in ["success", "sandbox"]:
                payment.status = Payment.Status.SUCCESS
                payment.order.status = Order.Status.PAID

                # 🔥 БЕЗПЕЧНИЙ ВИКЛИК CELERY (не зламає webhook, якщо Redis впав)
                try:
                    send_order_confirmation_email(payment.order.id)
                    print(f"✅ Email відправлено для замовлення #{payment.order.id}")
                except Exception as e:
                    print(f"⚠️ Помилка відправки email (не критично): {e}")

            elif payment_status in ["error", "failure"]:
                payment.status = Payment.Status.FAILURE
                payment.order.status = Order.Status.CANCELED
            elif payment_status == "wait_accept":
                payment.status = Payment.Status.PENDING

            payment.response_data = data
            payment.save()
            payment.order.save()

            print(
                f"✅ PAYMENT UPDATED: Order #{payment.order.id} "
                f"is now {payment.order.status}"
            )

        return Response({"success": True}, status=status.HTTP_200_OK)


class LiqPayResultView(APIView):
    """GET /api/payments/result/ - Куди повертається користувач після оплати"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Тут можна показати сторінку "Дякуємо за оплату!"
        return Response({"message": "Дякуємо за оплату!"})
