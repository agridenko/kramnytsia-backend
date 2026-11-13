from django.conf import settings
from django.core.mail import send_mail


def send_order_confirmation_email(order_id):
    """Відправка email підтвердження замовлення (синхронно)"""
    try:
        from apps.orders.models import Order

        order = Order.objects.get(id=order_id)

        subject = f"Підтвердження замовлення #{order.id}"
        message = (
            f"Дякуємо за ваше замовлення! "
            f"Номер замовлення: {order.id} "
            f"Сума: {order.total_with_delivery} UAH "
            f"Статус: {order.get_status_display()} "
            f"Ми почнемо збирати ваше замовлення найближчим часом. "
            f"З повагою, Команда Kramnytsia"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"❌ Помилка відправки email: {e}")
        raise
