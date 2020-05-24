"""Defines the admin interface for the test app, including inlines and filters."""

from django import forms
from django.contrib import admin
from django.shortcuts import reverse
from django.urls import path
from admin_auto_filters.filters import AutocompleteFilter, ACFilter
from .models import Food, Person, Collection, Book
from .views import FoodsThatAreFavorites


# hard code some user constants (must match fixture)
BASIC_USERNAME = 'bu'  # password is 'bu'
SHORTCUT_USERNAME = 'su'  # password is 'su'


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


class BookFilter(AutocompleteFilter):
    title = 'has book (manual)'
    field_name = 'book'
    rel_model = Collection
    parameter_name = 'book'


class FriendFilter(AutocompleteFilter):
    title = 'best friend (manual)'
    field_name = 'best_friend'
    rel_model = Person
    parameter_name = 'best_friend'


class FriendFriendFilter(AutocompleteFilter):
    title = 'best friend\'s best friend (manual)'
    field_name = 'best_friend'
    rel_model = Person
    parameter_name = 'best_friend__best_friend'


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


class FoodChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.alternate_name()


class FoodFilter(AutocompleteFilter):
    title = 'food (manual)'
    field_name = 'favorite_food'
    rel_model = Person
    parameter_name = 'favorite_food'
    form_field = FoodChoiceField

    def get_autocomplete_url(self, request, model_admin):
        return reverse('admin:foods_that_are_favorites')


class BestFriendOfFilter(AutocompleteFilter):
    title = 'best friend of (manual)'
    field_name = 'person'
    rel_model = Person
    parameter_name = 'person'


class AuthoredFilter(AutocompleteFilter):
    title = 'authored (manual)'
    field_name = 'book'
    rel_model = Person
    parameter_name = 'book'


class RevPersonFoodFilter(AutocompleteFilter):
    title = 'best friend of person with fav food (manual)'
    field_name = 'favorite_food'
    rel_model = Person
    parameter_name = 'person__favorite_food'


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


class CustomAdmin(admin.ModelAdmin):
    list_filter_auto = []

    class Media:
        css = {'all': ('custom.css',)}

    def get_list_filter(self, request):
        if request.user.username == BASIC_USERNAME:
            return self.list_filter
        elif request.user.username == SHORTCUT_USERNAME:
            return self.list_filter_auto
        else:
            raise ValueError('Unexpected username.')


@admin.register(Food)
class FoodAdmin(CustomAdmin):
    fields = ['id', 'name']
    inlines = [PersonInline]
    list_display = ['id', 'name']
    list_display_links = ['name']
    list_filter = [
        PersonFoodFilter,
    ]
    list_filter_auto = [
        ACFilter('favorite food of person (auto)', 'person'),
    ]
    ordering = ['id']
    readonly_fields = ['id']
    search_fields = ['id', 'name']


@admin.register(Collection)
class CollectionAdmin(CustomAdmin):
    autocomplete_fields = ['curators']
    fields = ['id', 'name', 'curators']
    inlines = [BookInline]
    list_display = ['id', 'name']
    list_display_links = ['name']
    list_filter = [
        CuratorsFilter,
        BookFilter,
    ]
    list_filter_auto = [
        ACFilter('curators (auto)', 'curators'),
        ACFilter('has book (auto)', 'book'),
    ]
    ordering = ['id']
    readonly_fields = ['id']
    search_fields = ['id', 'name', 'curators__name',
                     'book__title', 'book__author__name']


@admin.register(Person)
class PersonAdmin(CustomAdmin):
    autocomplete_fields = ['best_friend', 'siblings', 'favorite_food', 'curated_collections']
    fields = ['id', 'name', 'best_friend', 'siblings', 'favorite_food', 'curated_collections']
    inlines = [BookInline]
    list_display = ['id', 'name']
    list_display_links = ['name']
    list_filter = [
        FriendFilter,
        FriendFriendFilter,
        FriendFoodFilter,
        SiblingsFilter,
        FoodFilter,
        BestFriendOfFilter,
        AuthoredFilter,
        RevPersonFoodFilter,
    ]
    list_filter_auto = [
        ACFilter('best friend (auto)', 'best_friend'),
        ACFilter('best friend\'s best friend (auto)', 'best_friend__best_friend'),
        ACFilter('best friend\'s favorite food (auto)', 'best_friend__favorite_food'),
        ACFilter('siblings (auto)', 'siblings'),
        ACFilter('food (auto)', 'favorite_food', viewname='admin:foods_that_are_favorites', label_by='alternate_name'),
        ACFilter('best friend of (auto)', 'person'),
        ACFilter('authored (auto)', 'book'),
        ACFilter('best friend of person with fav food (auto)', 'person__favorite_food'),
        # ACFilter('curated_collections (auto)', 'curated_collections'),  # does not work...
    ]
    ordering = ['id']
    readonly_fields = ['id']
    search_fields = ['id', 'name', 'best_friend__name',
                     'favorite_food__name', 'siblings__name']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('foods_that_are_favorites/',
                 self.admin_site.admin_view(FoodsThatAreFavorites.as_view(model_admin=self)),
                 name='foods_that_are_favorites'),
        ]
        return custom_urls + urls


@admin.register(Book)
class BookAdmin(CustomAdmin):
    autocomplete_fields = ['author', 'coll']
    fields = ['isbn', 'title', 'author', 'coll']
    inlines = []
    list_display = ['isbn', 'title']
    list_display_links = ['title']
    list_filter = [
        AuthorFilter,
        CollectionFilter,
    ]
    list_filter_auto = [
        ACFilter('author (auto)', 'author'),
        ACFilter('collection (auto)', 'coll'),
    ]
    ordering = ['isbn']
    search_fields = ['isbn', 'title', 'author__name', 'coll__name']
