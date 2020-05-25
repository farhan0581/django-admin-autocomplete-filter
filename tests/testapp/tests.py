"""Define tests for the test app."""

import json
from django.contrib.admin.utils import flatten
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
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
    (Collection, 'curators', '1', 'id', (1,)),
    (Collection, 'curators', '3', 'id', ()),
    (Person, 'best_friend', '1', 'id', (2, 3)),
    (Person, 'best_friend__favorite_food', '1', 'id', (4,)),
    (Person, 'siblings', '2', 'id', (1, 3, 4)),
    (Person, 'favorite_food', '3', 'id', (3, 4)),
    (Book, 'author', '2', 'isbn', (42, )),
    (Book, 'coll', '2', 'isbn', (2357, )),
)


class RootTestCase(object):
    # fixtures = ['fixture.json']  # loading from data migration 0002

    @classmethod
    def setUpTestData(cls):
        cls.basic_user = User.objects.get(username=BASIC_USERNAME)
        cls.shortcut_user = User.objects.get(username=SHORTCUT_USERNAME)

    def test_endpoint(self):
        url = reverse('admin:foods_that_are_favorites')
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200, msg=str(url))
        data = json.loads(response.content)
        texts = set([item['text'] for item in data['results']])
        self.assertEqual(len(texts), 2, msg=str(texts))
        self.assertIn('spam', texts, msg=str(texts))
        self.assertIn('toast', texts, msg=str(texts))

    def test_admin_changelist_search(self):
        for model_name in MODEL_NAMES:
            with self.subTest(model_name=model_name):
                url = reverse('admin:testapp_%s_changelist' % model_name) + '?q=a'
                response = self.client.get(url, follow=False)
                self.assertEqual(response.status_code, 200, msg=str(url))

    def test_admin_autocomplete_load(self):
        for model_name in MODEL_NAMES:
            with self.subTest(model_name=model_name):
                url = reverse('admin:testapp_%s_autocomplete' % model_name)
                response = self.client.get(url, follow=False)
                self.assertContains(response, '"results"')

    def test_admin_changelist_filters(self):
        for model, key, val, field, pks in FILTER_STRINGS:
            model_name = name(model)
            with self.subTest(model_name=model_name):
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


class BasicTestCase(RootTestCase, TestCase):
    def setUp(self):
        self.client.force_login(self.basic_user)


class ShortcutTestCase(RootTestCase, TestCase):
    def setUp(self):
        self.client.force_login(self.shortcut_user)
