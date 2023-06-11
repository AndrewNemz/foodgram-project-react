import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Наполнение базы данных данными из ingredients.csv.
    Команда - pyhton manage.py fill_db.
    """
    def handle(self, *args, **options):

        file_path = 'data/ingredients.csv'
        print('Загрузка началась')

        with open(file_path, 'r', encoding='utf-8') as csv_file:
            ingredients = csv.reader(csv_file)

            for row in ingredients:
                name, measure_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measure_unit=measure_unit
                )

        print('Загрузка успешно завершена')
