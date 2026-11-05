import os
from celery import Celery

# Вказуємо Django, де шукати налаштування
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# Створюємо екземпляр Celery
app = Celery('kramnytsia')

# Завантажуємо налаштування з Django settings (префікс CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматично знаходимо задачі у всіх зареєстрованих застосунках
app.autodiscover_tasks()