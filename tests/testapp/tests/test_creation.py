"""Test the filter class creation."""

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, tag
from admin_auto_filters import filters


@tag('creation')
class CreationTestCase(TestCase):
    """Tests filter class creation."""

    def test_failed(self):

        class TestFilter(filters.AutocompleteFilter):
            pass

        self.assertRaises(ImproperlyConfigured, TestFilter, 'request', 'params', 'model', 'model_admin')

    def test_simple(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.title, 'Best Friend - Favorite Food')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__pk__exact')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_titled(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            title = 'A custom title'

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.title, 'A custom title')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__pk__exact')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_parameterized(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            parameter_name = 'bfff'

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'bfff')
        self.assertEqual(TestFilter.title, 'Best Friend - Favorite Food')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__pk__exact')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_triple(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            parameter_name = 'bfff'
            title = 'A custom title'

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'bfff')
        self.assertEqual(TestFilter.title, 'A custom title')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__pk__exact')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_parameter_tt(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            multi_select = True
            use_pk_exact = True

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.title, 'Best Friend - Favorite Food')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__pk__in')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_parameter_tf(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            multi_select = True
            use_pk_exact = False

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.title, 'Best Friend - Favorite Food')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__in')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_parameter_ft(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            multi_select = False
            use_pk_exact = True

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.title, 'Best Friend - Favorite Food')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__pk__exact')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_parameter_ff(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            multi_select = False
            use_pk_exact = False

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.title, 'Best Friend - Favorite Food')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_parameter_ft_pk(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            multi_select = False
            use_pk_exact = True
            field_pk = 'id'

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.title, 'Best Friend - Favorite Food')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__id__exact')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')

    def test_template(self):

        class TestFilter(filters.AutocompleteFilter):
            field_name = 'best_friend__favorite_food'
            template = 'custom-autocomplete-filter.html'

        self.assertEqual(TestFilter.field_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.parameter_name, 'best_friend__favorite_food')
        self.assertEqual(TestFilter.title, 'Best Friend - Favorite Food')
        self.assertEqual(TestFilter.get_query_parameter(), 'best_friend__favorite_food__pk__exact')
        self.assertEqual(TestFilter.get_ultimate_field_name(), 'favorite_food')
        self.assertEqual(TestFilter.template, 'custom-autocomplete-filter.html')
