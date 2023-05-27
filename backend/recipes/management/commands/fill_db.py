import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv в модель Ingredient'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        print('Загрузка данными базы данных началась.')
        file_path = 'data/ingredients.csv'
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)

            for row in reader:
                obj, created = Ingredient.objects.get_or_create(
                    name=row[0],
                    measure_unit=row[1],
                )

        print('Загрузка завершена.')
