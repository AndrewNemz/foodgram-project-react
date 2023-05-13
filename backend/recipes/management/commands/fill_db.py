import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    """
    Добавляем ингредиенты из файла CSV
    """
    help = 'Загркузка данных базы данных из csv-файла ингредиентов'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            default='ingredients.csv',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(DATA_ROOT, options['filename']),
                'r',
                encoding='utf-8'
            ) as f:
                data = csv.reader(f)
                for row in data:
                    name, measure_unit = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        measure_unit=measure_unit
                    )
        except FileNotFoundError:
            raise CommandError('Добавьте файл ingredients в директорию data')
        print('Загрузка успешно завершена.')
