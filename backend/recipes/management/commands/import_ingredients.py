import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            list_ingredients = [
                Ingredient(name=row[0], measurement_unit=row[1])
                for row in reader
            ]
        Ingredient.objects.bulk_create(list_ingredients)
