"""Define tests for the test app."""

import json
from django.contrib.admin.utils import flatten
from django.contrib.auth.models import User
from django.core import exceptions
from django.test import TestCase, tag
from django.urls import reverse
from admin_auto_filters import filters
from tests.testapp.admin import BASIC_USERNAME, SHORTCUT_USERNAME
from tests.testapp.models import Food, Collection, Person, Book


def name(model):
    """A repeatable way to get the formatted model name."""
    return model.__name__.replace('_', '').lower()


# a all of the models, and their names for convenience
MODELS = (Food, Collection, Person, Book)
MODEL_NAMES = tuple([name(model) for model in MODELS])


# a tuple of tuples with (model_name, key, val, field, pks)
# this must match data in fixture
FILTER_STRINGS = (
    (Food, 'person', '3', 'id', (3,)),
    (Food, 'people_with_this_least_fav_food', '3', 'id', (2,)),
    (Collection, 'curators', '1', 'id', (1,)),
    (Collection, 'curators', '3', 'id', ()),
    (Collection, 'book', '2357', 'id', (2,)),
    (Person, 'best_friend', '1', 'id', (2, 3)),
    (Person, 'twin', '1', 'id', (3,)),
    (Person, 'rev_twin', '3', 'id', (1,)),
    (Person, 'best_friend__best_friend', '1', 'id', (4,)),
    (Person, 'best_friend__favorite_food', '1', 'id', (4,)),
    (Person, 'siblings', '2', 'id', (1, 3, 4)),
    (Person, 'favorite_food', '3', 'id', (3, 4)),
    (Person, 'person', '3', 'id', (1,)),
    (Person, 'book', '1111', 'id', (4,)),
    (Person, 'person__favorite_food', '3', 'id', (1,2)),
    (Person, 'collection', '1', 'id', (1, 2)),
    (Book, 'author', '2', 'isbn', (42,)),
    (Book, 'coll', '2', 'isbn', (2357,)),
    (Book, 'people_with_this_fav_book', '4', 'isbn', (1234,)),
)


class RootTestCase(object):
    # fixtures = ['fixture.json']  # loading from data migration 0002

    @classmethod
    def setUpTestData(cls):
        cls.basic_user = User.objects.get(username=BASIC_USERNAME)
        cls.shortcut_user = User.objects.get(username=SHORTCUT_USERNAME)

    def test_endpoint(self):
        """
        Test that custom autocomplete endpoint functions and returns proper values.
        """
        url = reverse('admin:foods_that_are_favorites')
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200, msg=str(url))
        data = json.loads(response.content)
        texts = set([item['text'] for item in data['results']])
        self.assertEqual(len(texts), 2, msg=str(texts))
        self.assertIn('SPAM', texts, msg=str(texts))
        self.assertIn('TOAST', texts, msg=str(texts))

    def test_admin_changelist_search(self):
        """
        Test that the admin changelist page loads with a search query, at a basic level.
        Need selenium tests to fully check.
        """
        for model_name in MODEL_NAMES:
            with self.subTest(model_name=model_name):
                url = reverse('admin:testapp_%s_changelist' % model_name) + '?q=a'
                response = self.client.get(url, follow=False)
                self.assertContains(
                    response, '/static/custom.css',
                    html=False, msg_prefix=str(url)
                )

    def test_admin_autocomplete_load(self):
        """
        Test that the admin autocomplete endpoint loads.
        """
        for model_name in MODEL_NAMES:
            with self.subTest(model_name=model_name):
                url = reverse('admin:testapp_%s_autocomplete' % model_name)
                response = self.client.get(url, follow=False)
                self.assertContains(response, '"results"')

    def test_admin_changelist_filters(self):
        """
        Test that the admin changelist page loads with filters applied, at a basic level.
        Need selenium tests to fully check.
        """
        for model, key, val, field, pks in FILTER_STRINGS:
            model_name = name(model)
            with self.subTest(model_name=model_name, key=key, val=val, field=field):
                url = reverse('admin:testapp_%s_changelist' % model_name) + '?%s=%s' % (key, val)
                response = self.client.get(url, follow=False)
                # print(response.content.decode('utf-8'))
                self.assertEqual(response.status_code, 200, msg=str(url))
                all_pks = set(flatten(list(model.objects.values_list('pk'))))
                for pk in pks:
                    self.assertContains(
                        response, '<td class="field-%s">%s</td>' % (field, pk),
                        html=True, msg_prefix=str(url)
                    )
                for pk in all_pks - set(pks):
                    self.assertNotContains(
                        response, '<td class="field-%s">%s</td>' % (field, pk),
                        html=True, msg_prefix=str(url)
                    )

    def test_get_queryset_for_field(self):
        """
        Test the AutocompleteFilter.get_queryset_for_field method.
        """
        class TestFilter(filters.AutocompleteFilter):
            def __init__(self, *args, **kwargs):
                pass
        f = TestFilter()
        self.assertRaises(exceptions.FieldDoesNotExist,
                          f.get_queryset_for_field, Person, 'not_a_field')
        self.assertRaises(AttributeError,
                          f.get_queryset_for_field, Person, 'name')
        for field in ('best_friend', 'siblings', 'favorite_food',
                      'curated_collections', 'favorite_book', 'book'):
            with self.subTest(field=field):
                try:
                    qs = f.get_queryset_for_field(Person, field)
                except BaseException as e:
                    self.fail(str(e))
        try:
            qs = f.get_queryset_for_field(Book, 'people_with_this_fav_book')
        except BaseException as e:
            self.fail(str(e))


@tag('basic')
class BasicTestCase(RootTestCase, TestCase):
    def setUp(self):
        self.client.force_login(self.basic_user)


@tag('shortcut')
class ShortcutTestCase(RootTestCase, TestCase):
    def setUp(self):
        self.client.force_login(self.shortcut_user)
