from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import time


@shared_task
def send_order_confirmation_email(order_id: int):
    """
    Фонова задача для відправки email підтвердження замовлення.
    """
    # Імітуємо "важку" роботу (наприклад, генерацію PDF або повільний SMTP)
    time.sleep(3)

    # У реальному проєкті тут був би запит до БД:
    # from orders.models import Order
    # order = Order.objects.get(id=order_id)
    # email = order.user.email

    print(f"[CELERY] Відправляємо email підтвердження для замовлення #{order_id} на пошту...")

    # Для тесту використовуємо console backend (виведе email у термінал Django)
    send_mail(
        subject=f"Замовлення #{order_id} успішно оплачено!",
        message=f"Дякуємо за покупку! Ваше замовлення #{order_id} прийнято в обробку.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["test@example.com"],  # Заміни на реальну пошту для тесту
        fail_silently=False,
    )

    return f"Email для замовлення {order_id} відправлено"
