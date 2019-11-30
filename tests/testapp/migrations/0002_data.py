"""A data migration to load in fixtures."""

from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'fixture', app_label='testapp')


def unload_fixture(apps, schema_editor):
    Book = apps.get_model("location", "Book")
    Collection = apps.get_model("location", "Collection")
    Food = apps.get_model("location", "Food")
    Person = apps.get_model("location", "Person")
    Book.objects.all().delete()
    Collection.objects.all().delete()
    Food.objects.all().delete()
    Person.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
