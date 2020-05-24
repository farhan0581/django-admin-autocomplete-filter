"""Defines the models for the test app."""

from django.db import models


class Food(models.Model):
    name = models.CharField(max_length=100)

    def __repr__(self):
        return 'Food#' + str(self.id)

    def __str__(self):
        return self.name

    def alternate_name(self):
        return str(self.name).upper()


class Collection(models.Model):
    name = models.CharField(max_length=100)
    curators = models.ManyToManyField('Person', blank=True)

    def __repr__(self):
        return 'Collection#' + str(self.id)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=100)
    best_friend = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    siblings = models.ManyToManyField('self', blank=True)
    favorite_food = models.ForeignKey(Food, on_delete=models.CASCADE, blank=True, null=True)
    curated_collections = models.ManyToManyField(Collection, blank=True, db_table=Collection.curators.field.db_table)

    def __repr__(self):
        return 'Person#' + str(self.id)

    def __str__(self):
        return self.name


# Use this and curated_collections.db_table to set up reverse M2M
# See https://code.djangoproject.com/ticket/897
Person.curated_collections.through._meta.managed = False


class Book(models.Model):
    isbn = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)
    coll = models.ForeignKey(Collection, on_delete=models.CASCADE, blank=True, null=True)  # just for test purposes

    def __repr__(self):
        return 'Book#' + str(self.isbn)

    def __str__(self):
        return self.title
