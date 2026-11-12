"""Команда для наповнення бази тестовими даними.

Використання:
    python manage.py seed_data
    python manage.py seed_data --reset

Дані детерміновані: щоразу створюється однаковий набір.
Це важливо — інакше тести та скріншоти для README щоразу різні.
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.products.models import Category, Product

# ---------------------------------------------------------------------------
# ДАНІ
# ---------------------------------------------------------------------------

CATEGORIES: list[dict] = [
    {"name": "Стратегії", "slug": "strategy"},
    {"name": "Сімейні", "slug": "family"},
    {"name": "Партійні", "slug": "party"},
    {"name": "Коопераційні", "slug": "coop"},
    {"name": "Економічні", "slug": "economy"},
    {"name": "Для двох", "slug": "duel"},
    {"name": "Дитячі", "slug": "kids"},
]


PRODUCTS: list[dict] = [
    # ------------------------- СТРАТЕГІЇ -------------------------
    {
        "name": "Колонізатори",
        "slug": "colonizatory",
        "category": "strategy",
        "price": "1250.00",
        "stock": 12,
        "age_from": 10,
        "players_min": 3,
        "players_max": 4,
        "description": "Класична стратегія про заселення острова: "
        "ресурси, торгівля та дороги.",
    },
    {
        "name": "Крила",
        "slug": "kryla",
        "category": "strategy",
        "price": "1750.00",
        "stock": 5,
        "age_from": 10,
        "players_min": 1,
        "players_max": 5,
        "description": "Ви будуєте заповідник і залучаєте птахів. "
        "Прекрасні ілюстрації та моторошна математика.",
    },
    {
        "name": "7 Чудес",
        "slug": "7-chudes",
        "category": "strategy",
        "price": "1290.00",
        "stock": 6,
        "age_from": 10,
        "players_min": 3,
        "players_max": 7,
        "description": "Драфт-стратегія про розвиток античних міст у три епохи.",
    },
    {
        "name": "Терраформування Марса",
        "slug": "terraformuvannya-marsa",
        "category": "strategy",
        "price": "2050.00",
        "stock": 4,
        "age_from": 12,
        "players_min": 1,
        "players_max": 5,
        "description": "Ви — корпорація, що перетворює Марс на придатну "
        "для життя планету. Багато карт, багато мислення.",
    },
    {
        "name": "Еверделл",
        "slug": "everdell",
        "category": "strategy",
        "price": "2250.00",
        "stock": 3,
        "age_from": 10,
        "players_min": 1,
        "players_max": 4,
        "description": "Економічна стратегія про дерев'яне "
        "місто тварин із 3D-елементом.",
    },
    {
        "name": "Рут",
        "slug": "root",
        "category": "strategy",
        "price": "2550.00",
        "stock": 2,
        "age_from": 10,
        "players_min": 2,
        "players_max": 4,
        "description": "Асиметрична війна лісових фракцій: "
        "у кожної — свої правила гри.",
    },
    {
        "name": "Скит",
        "slug": "scythe",
        "category": "strategy",
        "price": "3100.00",
        "stock": 2,
        "age_from": 14,
        "players_min": 1,
        "players_max": 7,
        "description": "Альтернативна історія Європи 1920-х: "
        "ресурси, мехи та наполеглива дипломатія.",
    },
    {
        "name": "Малий світ",
        "slug": "malyi-svit",
        "category": "strategy",
        "price": "1450.00",
        "stock": 5,
        "age_from": 10,
        "players_min": 2,
        "players_max": 5,
        "description": "Фентезійні раси захоплюють світ, а потім змушені тікати далі.",
    },
    {
        "name": "Цитаделі",
        "slug": "tsytadeli",
        "category": "strategy",
        "price": "940.00",
        "stock": 8,
        "age_from": 10,
        "players_min": 2,
        "players_max": 8,
        "description": "Коротка партія про будівництво міста та читання суперників.",
    },
    {
        "name": "Колонізатори: Міста та мешканці",
        "slug": "colonizatory-mista",
        "category": "strategy",
        "price": "1380.00",
        "stock": 6,
        "age_from": 10,
        "players_min": 2,
        "players_max": 4,
        "description": "Розширення класики: міста, ринок і варіант для двох гравців.",
    },
    {
        "name": "Талісман",
        "slug": "talisman",
        "category": "strategy",
        "price": "1250.00",
        "stock": 0,  # спеціально 0 — щоб перевірити is_available
        "age_from": 9,
        "players_min": 2,
        "players_max": 6,
        "description": "Пригодницький забіг до Корони Володарства "
        "з боями та артефактами.",
    },
    {
        "name": "Імперія Сутінків",
        "slug": "imperiia-sutiniv",
        "category": "strategy",
        "price": "6200.00",
        "stock": 1,
        "age_from": 14,
        "players_min": 3,
        "players_max": 6,
        "description": "Велетенська космічна епопея на 6+ годин. "
        "Для тих, хто справді любить ігри.",
    },
    # ------------------------- СІМЕЙНІ -------------------------
    {
        "name": "Каркассон",
        "slug": "karkason",
        "category": "family",
        "price": "950.00",
        "stock": 20,
        "age_from": 7,
        "players_min": 2,
        "players_max": 5,
        "description": "Ви викладаєте плитки й будуєте дороги, "
        "міста та поля. Ідеальна гра для вечері з родиною.",
    },
    {
        "name": "Білет на поїзд",
        "slug": "bilet-na-poyizd",
        "category": "family",
        "price": "1450.00",
        "stock": 8,
        "age_from": 8,
        "players_min": 2,
        "players_max": 5,
        "description": "Збирайте вагони та будуйте залничні маршрути через континент.",
    },
    {
        "name": "Діксіт",
        "slug": "diksyt",
        "category": "family",
        "price": "980.00",
        "stock": 10,
        "age_from": 8,
        "players_min": 3,
        "players_max": 6,
        "description": "Гра на асоціації: одна казкова карта, десятки тлумачень.",
    },
    {
        "name": "Азул",
        "slug": "azul",
        "category": "family",
        "price": "1050.00",
        "stock": 9,
        "age_from": 8,
        "players_min": 2,
        "players_max": 4,
        "description": "Виkladіть керамічну плитку в мозаїку королівського палацу. "
        "Красива і підступна.",
    },
    {
        "name": "Кінгдоміно",
        "slug": "kingdomino",
        "category": "family",
        "price": "720.00",
        "stock": 18,
        "age_from": 8,
        "players_min": 2,
        "players_max": 4,
        "description": "Доміно, з якого ви будуєте королівство. 20 хвилин — і готово.",
    },
    {
        "name": "Каскадія",
        "slug": "kaskadiia",
        "category": "family",
        "price": "1320.00",
        "stock": 6,
        "age_from": 10,
        "players_min": 1,
        "players_max": 4,
        "description": "Лосось, лисиці та ведмеді у спокійному пазлі про екосистему.",
    },
    {
        "name": "Білет на поїзд: Північ",
        "slug": "bilet-na-poyizd-pivnich",
        "category": "family",
        "price": "1620.00",
        "stock": 5,
        "age_from": 8,
        "players_min": 2,
        "players_max": 5,
        "description": "Версія про Скандинавію з тунелями та поромними переправами.",
    },
    {
        "name": "Діксіт: Одисея",
        "slug": "diksyt-odiseia",
        "category": "family",
        "price": "1120.00",
        "stock": 7,
        "age_from": 8,
        "players_min": 3,
        "players_max": 6,
        "description": "Нова колода казкових карт для класичних асоціацій.",
    },
    {
        "name": "Шахраї з Кведлінбурга",
        "slug": "shakhrai-z-kvedlinburha",
        "category": "family",
        "price": "890.00",
        "stock": 9,
        "age_from": 8,
        "players_min": 2,
        "players_max": 4,
        "description": "Варіація на тему лото, де кожен намагається "
        "зібрати мішечок і не вибухнути.",
    },
    {
        "name": "Монополія",
        "slug": "monopoliia",
        "category": "family",
        "price": "1490.00",
        "stock": 15,
        "age_from": 8,
        "players_min": 2,
        "players_max": 6,
        "description": "Класика про нерухомість, банки та зіпсовані сімейні стосунки.",
    },
    # ------------------------- ПАРТІЙНІ -------------------------
    {
        "name": "Кодові імена",
        "slug": "kodovi-imena",
        "category": "party",
        "price": "620.00",
        "stock": 25,
        "age_from": 10,
        "players_min": 2,
        "players_max": 8,
        "description": "Дві команди агентів, одне слово-підказка і тонкі асоціації.",
    },
    {
        "name": "Саші Го",
        "slug": "sashi-go",
        "category": "party",
        "price": "360.00",
        "stock": 30,
        "age_from": 6,
        "players_min": 2,
        "players_max": 5,
        "description": "Швидка гра на збирання наборів суші. "
        "Правилах — хвилина, партія — 15 хвилин.",
    },
    {
        "name": "Манчкін",
        "slug": "manchkin",
        "category": "party",
        "price": "540.00",
        "stock": 22,
        "age_from": 10,
        "players_min": 3,
        "players_max": 6,
        "description": "Пародія на підземелля, де головне — підставити друзів.",
    },
    {
        "name": "Вибух котенят",
        "slug": "vybukh-koteniati",
        "category": "party",
        "price": "690.00",
        "stock": 19,
        "age_from": 8,
        "players_min": 2,
        "players_max": 5,
        "description": "Руська рулетка з картами: тягніть, поки не вибухне.",
    },
    # ------------------------- КООПЕРАЦІЙНІ -------------------------
    {
        "name": "Пандемія",
        "slug": "pandemia",
        "category": "coop",
        "price": "1150.00",
        "stock": 7,
        "age_from": 8,
        "players_min": 2,
        "players_max": 4,
        "description": "Ви граєте не проти один одного, "
        "а проти хвороби. Програєте — разом.",
    },
    {
        "name": "Острів духів",
        "slug": "ostriv-dukhiv",
        "category": "coop",
        "price": "2650.00",
        "stock": 2,
        "age_from": 14,
        "players_min": 1,
        "players_max": 4,
        "description": "Жорстока кооперативна стратегія про "
        "захист острова від духів помсти.",
    },
    {
        "name": "Анлок!",
        "slug": "unlock",
        "category": "coop",
        "price": "760.00",
        "stock": 12,
        "age_from": 10,
        "players_min": 2,
        "players_max": 6,
        "description": "Ескейп-рум на столі: карти, коди та таймер на 60 хвилин.",
    },
    {
        "name": "Глоухейвен",
        "slug": "glookheiven",
        "category": "coop",
        "price": "5600.00",
        "stock": 1,
        "age_from": 14,
        "players_min": 1,
        "players_max": 4,
        "description": "Кампанійний бойовик із сотнями сценаріїв. "
        "Гра на місяці, а не на вечір.",
    },
    # ------------------------- ЕКОНОМІЧНІ -------------------------
    {
        "name": "Сплендор",
        "slug": "splendor",
        "category": "economy",
        "price": "990.00",
        "stock": 14,
        "age_from": 8,
        "players_min": 2,
        "players_max": 4,
        "description": "Гірко, швидко й елегантно: "
        "коштовності, карти та оптимізація ходів.",
    },
    {
        "name": "Брас: Бірмінгем",
        "slug": "brass-birmingham",
        "category": "economy",
        "price": "2850.00",
        "stock": 0,  # спеціально 0
        "age_from": 14,
        "players_min": 2,
        "players_max": 4,
        "description": "Промислова революція, вугілля, "
        "залізниця й неймовірна глибина планування.",
    },
    {
        "name": "Агрікола",
        "slug": "ahrikola",
        "category": "economy",
        "price": "1850.00",
        "stock": 3,
        "age_from": 12,
        "players_min": 1,
        "players_max": 5,
        "description": "Фермерська стратегія, де не вистачає всього: "
        "їжі, деревa, робочих рук.",
    },
    {
        "name": "Пуерто-Ріко",
        "slug": "puerto-riko",
        "category": "economy",
        "price": "1650.00",
        "stock": 4,
        "age_from": 12,
        "players_min": 3,
        "players_max": 5,
        "description": "Вибір ролей, плантації та торгівля. Еталон економічної гри.",
    },
    # ------------------------- ДЛЯ ДВОХ -------------------------
    {
        "name": "7 Чудес: Дуель",
        "slug": "7-chudes-duel",
        "category": "duel",
        "price": "1150.00",
        "stock": 11,
        "age_from": 10,
        "players_min": 2,
        "players_max": 2,
        "description": "Одна з найкращих ігор саме для двох: "
        "війна, наука й цивілізація.",
    },
    {
        "name": "Кодові імена: Дует",
        "slug": "kodovi-imena-duet",
        "category": "duel",
        "price": "640.00",
        "stock": 13,
        "age_from": 10,
        "players_min": 2,
        "players_max": 2,
        "description": "Кооперативна версія Кодових імен: ви проти поля карток.",
    },
    {
        "name": "Патчворк",
        "slug": "patchwork",
        "category": "duel",
        "price": "780.00",
        "stock": 9,
        "age_from": 8,
        "players_min": 2,
        "players_max": 2,
        "description": "Ви зшиваєте ковдру й рахуєте кожну кнопку та кожну хвилину.",
    },
    {
        "name": "Джайпур",
        "slug": "dzhaipur",
        "category": "duel",
        "price": "620.00",
        "stock": 16,
        "age_from": 8,
        "players_min": 2,
        "players_max": 2,
        "description": "Торгівля тканинами й верблюдами. Ризикуй або забирай прибуток.",
    },
    # ------------------------- ДИТЯЧІ -------------------------
    {
        "name": "Уно",
        "slug": "uno",
        "category": "kids",
        "price": "320.00",
        "stock": 40,
        "age_from": 6,
        "players_min": 2,
        "players_max": 10,
        "description": "Позбався всіх карт і не забудь крикнути «Уно!».",
    },
    {
        "name": "Доббль",
        "slug": "dobbly",
        "category": "kids",
        "price": "420.00",
        "stock": 35,
        "age_from": 6,
        "players_min": 2,
        "players_max": 8,
        "description": "Знайди спільний символ швидше за всіх. Реакція вирішує все.",
    },
    {
        "name": "Лови рибу",
        "slug": "lovy-rybu",
        "category": "kids",
        "price": "380.00",
        "stock": 28,
        "age_from": 3,
        "players_min": 2,
        "players_max": 4,
        "description": "Магнітна вудка та рибки з відерцем. "
        "Перша настолка для найменших.",
    },
    {
        "name": "Вежа",
        "slug": "vezha",
        "category": "kids",
        "price": "450.00",
        "stock": 21,
        "age_from": 6,
        "players_min": 1,
        "players_max": 6,
        "description": "Дерев'яні блоки, рівновага та дрожащі руки.",
    },
]


# ---------------------------------------------------------------------------
# КОМАНДА
# ---------------------------------------------------------------------------


class Command(BaseCommand):
    help = "Створює тестові категорії та товари для локальної розробки."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Спершу видалити всі товари та категорії. ЗАБОРОНЕНО на продакшні!",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # 0. БЕЗПЕКА: Забороняємо --reset на продакшні
        if options["reset"] and not settings.DEBUG:
            raise CommandError(
                "Використання --reset на продакшні (DEBUG=False) "
                "заборонено з міркувань безпеки!"
            )

        if options["reset"]:
            deleted_products, _ = Product.objects.all().delete()
            deleted_categories, _ = Category.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"🧹 Очищено базу: {deleted_products} товарів, "
                    f"{deleted_categories} категорій."
                )
            )

        # 1. Категорії -------------------------------------------------
        categories: dict[str, Category] = {}
        created_categories = 0

        for item in CATEGORIES:
            # Шукаємо за унікальним slug. Якщо немає - створюємо з defaults.
            category, created = Category.objects.get_or_create(
                slug=item["slug"],
                defaults={"name": item["name"]},
            )
            categories[category.slug] = category
            if created:
                created_categories += 1

        # 2. Товари ----------------------------------------------------
        created_products = 0
        existing_products = 0

        for item in PRODUCTS:
            payload = dict(item)  # копія, щоб не псувати оригінал
            category_slug = payload.pop(
                "category"
            )  # це НЕ поле моделі, а ключ для пошуку

            category = categories.get(category_slug)
            if category is None:
                # Замість крашу всього деплою, просто пропускаємо товар і йдемо далі
                self.stdout.write(
                    self.style.ERROR(
                        f"⚠️ Пропущено товар '{payload.get('name', 'Невідомо')}'. "
                        f"Невідома категорія: {category_slug}"
                    )
                )
                continue

            payload["category"] = category  # а це вже поле моделі
            slug = payload.pop("slug")

            # 💡 ВАЖЛИВО ДЛЯ RENDER: Якщо у тебе є поле 'image',
            # і файлів немає на сервері, розкоментуй наступний рядок,
            # щоб уникнути помилок "File not found" при створенні.
            payload.pop("image", None)

            product, created = Product.objects.get_or_create(
                slug=slug, defaults=payload
            )

            if created:
                created_products += 1
            else:
                existing_products += 1

            # 3. Створюємо суперюзера (якщо його немає)
            from django.contrib.auth import get_user_model

            User = get_user_model()

            # Змінити на безпечніший у продакшені
            # (краще для продакшену взагалі не застосовувати) !!!
            admin_email = "admin@admin.com"
            admin_password = "123456789"

            if not User.objects.filter(email=admin_email).exists():
                User.objects.create_superuser(
                    email=admin_email,
                    password=admin_password,
                    first_name="Admin",
                    last_name="Kramnytsia",
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"👤 Суперюзер створено: {admin_email} / {admin_password}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ Суперюзер {admin_email} вже існує, пропускаємо."
                    )
                )

            # 4. Звіт ------------------------------------------------------
            total = Product.objects.count()
            available = Product.objects.filter(stock__gt=0).count()

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Готово. Категорій створено: {created_categories}. "
                    f"Товарів створено: {created_products}, "
                    f"вже існувало: {existing_products}."
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"📊 У базі тепер: {total} товарів, у наявності: {available}."
                )
            )
