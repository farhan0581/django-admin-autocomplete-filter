"""Defines custom autocompletion views for the test app."""

from django.db.models import Q
from admin_auto_filters.views import AutocompleteJsonView
from .models import Food


class FoodsThatAreFavorites(AutocompleteJsonView):
    """List only foods that are someone's favorite."""

    @staticmethod
    def display_text(obj):
        return obj.alternate_name()

    def get_queryset(self):

        # Get items in use (would need to use related_query_name if applicable)
        foods = list(Food.objects.filter(person__isnull=False).values_list('id'))
        foods = list(set([item for sublist in foods for item in sublist if item is not None]))

        # Construct query
        qs = Food.objects.filter(id__in=foods).only('id', 'name')
        for bit in self.term.split(' '):
            qs = qs.filter(Q(id__icontains=bit) | Q(name__icontains=bit))
        qs = qs.order_by('name')  #.distinct()
        return qs
