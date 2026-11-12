# 1. Використовуємо офіційний легкий образ Python 3.12
FROM python:3.12-slim

# 2. Вимикаємо створення .pyc файлів та буферизацію виводу (краще для Docker)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# 4. Встановлюємо системні залежності (потрібні для деяких Python-пакетів)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Копіюємо файл залежностей і встановлюємо їх
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Копіюємо весь код проєкту в контейнер
COPY . .

# 7. Збираємо статичні файли. Якщо цього не зробити, адмінка та API docs будуть ламатися (500/404)
RUN python manage.py collectstatic --noinput || echo "Static files collection skipped or failed, continuing..."


# Для запуску на Render
CMD python manage.py migrate --noinput && \
    python manage.py seed_data && \
    gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
