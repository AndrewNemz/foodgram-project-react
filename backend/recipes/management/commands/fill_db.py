import contextlib
import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Наполнение базы данных данными из ingredients.csv.
    Команда - pyhton manage.py fill_db.
    """
    def handle(self, *args, **options):

        p = 'data/'
        print('Загрузка началась')

        with contextlib.ExitStack() as stack:
            ingredients = csv.DictReader(
                stack.enter_context(open(f'{p}ingredients.csv', 'r'))
            )

            for row in ingredients:
                name, measure_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measure_unit=measure_unit
                )

        print('Загрузка успешно завершена')
