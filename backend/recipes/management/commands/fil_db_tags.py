import csv

from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """
    Наполнение базы данных данными из ingredients.csv.
    Команда - pyhton manage.py fill_db_tags.
    """
    def handle(self, *args, **options):

        file_path = 'data/tags.csv'
        print('Загрузка началась')

        with open(file_path, 'r', encoding='utf-8') as csv_file:
            tags = csv.reader(csv_file)

            for row in tags:
                name, color, slug = row
                Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug
                )

        print('Загрузка успешно завершена')
