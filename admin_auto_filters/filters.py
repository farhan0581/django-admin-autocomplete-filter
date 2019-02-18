from django.contrib.admin.widgets import AutocompleteSelect
from django import forms
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.forms.widgets import Media, MEDIA_TYPES


class AutocompleteFilter(admin.SimpleListFilter):
    template = 'autocomplete-filter.html'
    title = ''
    field_name = ''
    field_pk = 'id'
    is_placeholder_title = False
    widget_attrs = {}
    rel_model = None

    class Media:
        js = (
            'js/autocomplete_filter_qs.js',
        )
        css = {
            'screen': (
                'css/autocomplete-fix.css',
            ),
        }

    def __init__(self, request, params, model, model_admin):
        self.parameter_name = '{}__{}__exact'.format(self.field_name, self.field_pk)
        super().__init__(request, params, model, model_admin)

        if self.rel_model:
            model = self.rel_model

        remote_field = model._meta.get_field(self.field_name).remote_field

        widget = AutocompleteSelect(remote_field, model_admin.admin_site)
        field = forms.ModelChoiceField(
            queryset=self.get_queryset_for_field(model, self.field_name),
            widget=widget,
            required=False
        )

        self._add_media(model_admin, widget)

        attrs = self.widget_attrs.copy()
        attrs['id'] = 'id-%s-dal-filter' % self.field_name
        if self.is_placeholder_title:
            attrs['data-placeholder'] = self.title
        self.rendered_widget = field.widget.render(
            name=self.parameter_name,
            value=self.used_parameters.get(self.parameter_name, ''),
            attrs=attrs
        )

    def get_queryset_for_field(self, model, name):
        return getattr(model, name).get_queryset()

    def _add_media(self, model_admin, widget):

        if not hasattr(model_admin, 'Media'):
            raise ImproperlyConfigured('Add empty Media class to %s. Sorry about this bug.' % model_admin)

        def _get_media(obj):
            return Media(media=getattr(obj, 'Media', None))

        media = _get_media(model_admin) + widget.media + _get_media(AutocompleteFilter) + _get_media(self)

        for name in MEDIA_TYPES:
            setattr(model_admin.Media, name, getattr(media, "_" + name))

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.parameter_name: self.value()})
        else:
            return queryset