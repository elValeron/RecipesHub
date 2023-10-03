import csv

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Загрузка данных в бд из файлов csv."""
    help = 'Загрузка данных из csv файла'

    def handle(self, *args, **options):
        try:
            with open('ingredients.csv', 'r', encoding='utf-8') as file:
                field_names = ['name', 'measurement_unit']
                reader = csv.DictReader(file, fieldnames=field_names)
                for row in reader:
                    obj = Ingredient.objects.get_or_create(
                        name=row['name'],
                        measurement_unit=row['measurement_unit']
                    )
            with open('tags.csv', 'r', encoding='utf-8') as file:
                for row in csv.DictReader(file):
                    obj = Tag.objects.get_or_create(
                        name=row['name'],
                        color=row['color'],
                        slug=row['slug']
                    )
        except ObjectDoesNotExist:
            obj = Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            obj.save()
        print('Данные успешно загружены')
