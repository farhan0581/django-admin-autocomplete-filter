"""Defines the admin interface for the test app, including inlines and filters."""

from django.contrib import admin
from django.shortcuts import reverse
from django.urls import path
from admin_auto_filters.filters import AutocompleteFilter
from .models import Food, Person, Collection, Book
from .views import FoodsThatAreFavorites


class PersonFoodFilter(AutocompleteFilter):
    title = 'favorite food of person (manual)'
    field_name = 'person'
    rel_model = Food
    parameter_name = 'person'


class CuratorsFilter(AutocompleteFilter):
    title = 'curators (manual)'
    field_name = 'curators'
    rel_model = Collection
    parameter_name = 'curators'


class FriendFilter(AutocompleteFilter):
    title = 'best friend (manual)'
    field_name = 'best_friend'
    rel_model = Person
    parameter_name = 'best_friend'


class FriendFoodFilter(AutocompleteFilter):
    title = 'best friend\'s favorite food (manual)'
    field_name = 'favorite_food'
    rel_model = Person
    parameter_name = 'best_friend__favorite_food'


class SiblingsFilter(AutocompleteFilter):
    title = 'siblings (manual)'
    field_name = 'siblings'
    rel_model = Person
    parameter_name = 'siblings'


class FoodFilter(AutocompleteFilter):
    title = 'food (manual)'
    field_name = 'favorite_food'
    rel_model = Person
    parameter_name = 'favorite_food'

    def get_autocomplete_url(self, request, model_admin):
        return reverse('admin:foods_that_are_favorites')


class AuthorFilter(AutocompleteFilter):
    title = 'author (manual)'
    field_name = 'author'
    rel_model = Book
    parameter_name = 'author'


class CollectionFilter(AutocompleteFilter):
    title = 'collection (manual)'
    field_name = 'coll'
    rel_model = Book
    parameter_name = 'coll'


class FoodInline(admin.TabularInline):
    extra = 0
    fields = ['id', 'name']
    model = Food


class CollectionInline(admin.TabularInline):
    extra = 0
    fields = ['id', 'name']
    model = Collection


class PersonInline(admin.TabularInline):
    extra = 0
    fields = ['id', 'name']
    model = Person


class BookInline(admin.TabularInline):
    extra = 0
    fields = ['isbn', 'title']
    model = Book


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    fields = ['id', 'name']
    inlines = [PersonInline]
    list_display = ['id', 'name']
    list_display_links = ['name']
    list_filter = [
        PersonFoodFilter,
    ]
    ordering = ['id']
    readonly_fields = ['id']
    search_fields = ['id', 'name']

    class Media:
        pass


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['curators']
    fields = ['id', 'name', 'curators']
    inlines = [BookInline]
    list_display = ['id', 'name']
    list_display_links = ['name']
    list_filter = [
        CuratorsFilter
    ]
    ordering = ['id']
    readonly_fields = ['id']
    search_fields = ['id', 'name', 'curators__name',
                     'book__title', 'book__author__name']

    class Media:
        pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    autocomplete_fields = ['best_friend', 'siblings', 'favorite_food', 'curated_collections']
    fields = ['id', 'name', 'best_friend', 'siblings', 'favorite_food', 'curated_collections']
    inlines = [BookInline]
    list_display = ['id', 'name']
    list_display_links = ['name']
    list_filter = [
        FriendFilter,
        FriendFoodFilter,
        SiblingsFilter,
        FoodFilter,
    ]
    ordering = ['id']
    readonly_fields = ['id']
    search_fields = ['id', 'name', 'best_friend__name',
                     'favorite_food__name', 'siblings__name']

    class Media:
        pass

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('foods_that_are_favorites/',
                 self.admin_site.admin_view(FoodsThatAreFavorites.as_view(model_admin=self)),
                 name='foods_that_are_favorites'),
        ]
        return custom_urls + urls


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    autocomplete_fields = ['author', 'coll']
    fields = ['isbn', 'title', 'author', 'coll']
    inlines = []
    list_display = ['isbn', 'title']
    list_display_links = ['title']
    list_filter = [
        AuthorFilter,
        CollectionFilter,
    ]
    ordering = ['isbn']
    search_fields = ['isbn', 'title', 'author__name', 'coll__name']

    class Media:
        pass
