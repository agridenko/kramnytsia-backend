# 🛒 Kramnytsia Backend API

![Django CI](https://github.com/agridenko/kramnytsia-backend/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-76%25-yellowgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-REST%20Framework-092E20)
![License](https://img.shields.io/badge/license-MIT-green)

Потужний, масштабований та безпечний REST API бекенд для інтернет-магазину. Проєкт розроблений з використанням сучасних практик, включаючи асинхронні задачі, інтеграцію з платіжними системами та автоматизований CI/CD.

🔗 **Live API:** [https://kramnytsia-backend.onrender.com/api/docs/](https://kramnytsia-backend.onrender.com/api/docs/)

---

## ✨ Основні можливості (Features)

- 🔐 **Автентифікація та авторизація:** JWT-токени, ролі користувачів, безпечне хешування паролів.
- 🛍️ **Каталог товарів:** Категорії, товари, фільтрація, пошук, пагінація.
- 🛒 **Кошик та замовлення:** Додавання товарів, перевірка залишків (stock), оформлення замовлень з транзакційною цілісністю.
- 💳 **Інтеграція з LiqPay:** Створення платежів, обробка webhook-ів, перевірка підписів, зміна статусів замовлень.
- 🚚 **Інтеграція з Новою Поштою:** Отримання міст та відділень, розрахунок вартості доставки з кешуванням відповідей.
- ⚡ **Асинхронність (Celery + Redis):** Фонові задачі для відправки email-підтверджень без блокування основного потоку.
- 🧪 **Тестування:** Покриття коду на ~76% за допомогою `pytest`, `pytest-django` та `factory-boy`.
- 🚀 **CI/CD та Деплой:** Автоматичний запуск тестів через GitHub Actions та деплой на Render у Docker-контейнерах.

---

## 🛠 Технологічний стек (Tech Stack)

| Категорія | Технології |
| :--- | :--- |
| **Мова** | Python 3.12 |
| **Фреймворк** | Django 6.x, Django REST Framework (DRF) |
| **База даних** | PostgreSQL |
| **Кешування та черги** | Redis, Celery |
| **Контейнеризація** | Docker, Docker Compose |
| **Тестування** | Pytest, pytest-cov, Factory Boy |
| **CI/CD** | GitHub Actions |
| **Хостинг** | Render |
| **Документація API** | drf-spectacular (Swagger / OpenAPI 3.0) |

---

## 🚀 Швидкий старт (Local Development)

Для локального запуску використовується Docker, що гарантує однакове середовище розробки.

### 1. Клонування репозиторію
```bash
git clone https://github.com/[твій-нік]/kramnytsia-backend.git
cd kramnytsia-backend
```
### 2. Налаштування змінних оточення
Створіть файл .env на основі прикладу:
```bash
cp .env.example .env
```
### 3. Запуск контейнерів
```bash
docker-compose up --build
```
Після запуску API буде доступне за адресою: http://127.0.0.1:8000/api/docs/

### 4. Наповнення бази даних (Seed Data)
Щоб додати тестові категорії та товари в БД:
```bash
docker-compose exec web python manage.py seed_data
```
(Скрипт ідемпотентний: він безпечно пропускає вже існуючі записи).


## 🧪 Тестування
Проєкт покритий unit та integration тестами. Для запуску:
```bash
# Запуск всіх тестів
docker-compose exec web pytest

# Запуск з звітом про покриття коду
docker-compose exec web pytest --cov=cart --cov=delivery --cov=orders --cov=products --cov=payments --cov-report=term-missing
```

## 📂 Структура проєкту
```text
kramnytsia-backend/
├── .github/workflows/      # GitHub Actions (CI/CD)
├── apps/                   # БІЗНЕС-ЛОГІКА
│   ├── __init__.py
│   ├── cart/               # Кошик
│   ├── delivery/           # Інтеграція з Новою Поштою
│   ├── orders/             # Замовлення та чекаут
│   ├── payments/           # Інтеграція з LiqPay
│   ├── products/           # Товари та категорії
│   └── users/              # Кастомна модель користувача
├── config/                 # НАЛАШТУВАННЯ ПРОЄКТУ
│   ├── settings/           # base.py, dev.py, prod.py налаштування
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── media/                  # Завантажені користувачами файли
├── staticfiles/            # Зібрана статика для продакшну
├── .env.example            
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── Procfile
├── pytest.ini
├── README.md
└── requirements.txt
```

## 🌍 Деплой (Production)
Проєкт автоматично деплоїться на **Render** при кожному push у гілку main/develop.

1. **CI/CD:** GitHub Actions автоматично запускає pytest перед деплоєм.
2. **База даних:** Використовується керований PostgreSQL від Render.
3. **Міграції та Seed:** Автоматично виконуються в Dockerfile перед стартом Gunicorn.
4. **Статика:** Обробляється через WhiteNoise.

## ⚙️ Змінні оточення (.env.example)
Ось основні змінні, які потребують налаштування:
```dotenv
# Django
SECRET_KEY=your-super-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DATABASE_URL=postgres://user:password@db:5432/dbname

# Redis & Celery
CELERY_BROKER_URL=redis://redis:6379/0

# External APIs
LIQPAY_PUBLIC_KEY=sandbox_...
LIQPAY_PRIVATE_KEY=sandbox_...
LIQPAY_SANDBOX=1
NOVA_POSHTA_API_KEY=your_np_api_key
```

## 🤝 Внесок у проєкт (Contributing)
1. Зробіть Fork репозиторію.
2. Створіть гілку для вашої фічі (git checkout -b feature/AmazingFeature).
3. Закомітьте зміни (git commit -m 'Add some AmazingFeature').
4. Зробіть Push у гілку (git push origin feature/AmazingFeature).
5. Відкрийте Pull Request.

## 📄 Ліцензія
Цей проєкт розповсюджується під ліцензією [MIT](LICENSE).