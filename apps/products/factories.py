import factory
from factory.django import DjangoModelFactory

from .models import Category, Product


class CategoryFactory(DjangoModelFactory):
    """Фабрика для створення тестових категорій."""

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Категорія {n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class ProductFactory(DjangoModelFactory):
    """Фабрика для створення тестових товарів."""

    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Товар {n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    description = factory.Faker("text", max_nb_chars=200, locale="uk_UA")
    price = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=100,
        max_value=5000,
    )
    stock = factory.Faker("random_int", min=0, max=100)
    age_from = factory.Faker("random_int", min=3, max=18)
    players_min = factory.Faker("random_int", min=1, max=4)
    players_max = factory.Faker("random_int", min=2, max=8)
    category = factory.SubFactory(CategoryFactory)
