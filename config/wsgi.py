import os
import traceback
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

try:
    # Спробуємо запустити додаток
    application = get_wsgi_application()
    print("✅ Django успішно запустився!")
except Exception as e:
    # Якщо щось пішло не так, виведемо повну помилку в логи Render
    print("❌ КРИТИЧНА ПОМИЛКА ПРИ ЗАПУСКУ DJANGO:")
    traceback.print_exc()
    raise e