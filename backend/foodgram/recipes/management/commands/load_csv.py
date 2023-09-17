import csv

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из csv файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Путь к csv файлу'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        self.import_data(csv_file)

    def import_data(self, csv_file):
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                name = row[0]
                measurement_unit = row[1]

                try:
                    obj = Ingredient.objects.get(name=name)
                    obj.measurement_unit = measurement_unit
                    obj.save()
                except ObjectDoesNotExist:
                    obj = Ingredient(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                    obj.save()
            print(f'Загрузка данных из файла {file.name} завершена')
