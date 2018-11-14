from django.contrib.admin.widgets import AutocompleteSelect
from django import forms
from django.contrib import admin
from django.conf import settings
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS, get_language
from django.forms.widgets import Media, MEDIA_TYPES


class AutocompleteFilter(admin.SimpleListFilter):
    template = 'autocomplete-filter.html'
    title = ''
    field_name = ''
    is_placeholder_title = False
    widget_attrs = {}
    rel_model = None

    class Media:
        extra = '' if settings.DEBUG else '.min'
        i18n_name = SELECT2_TRANSLATIONS.get(get_language())
        i18n_file = ('admin/js/vendor/select2/i18n/%s.js' % i18n_name,) if i18n_name else ()
        js = (
                'admin/js/vendor/select2/select2.full%s.js' % extra,
            ) + i18n_file + (
                'admin/js/jquery.init.js',
                'admin/js/autocomplete.js',
                'js/autocomplete_filter_qs.js',
            )
        css={
                'screen': (
                    'admin/css/vendor/select2/select2%s.css' % extra,
                    'admin/css/autocomplete.css',
                    'css/autocomplete-fix.css',
                ),
            }

    def __init__(self, request, params, model, model_admin):
        if self.parameter_name:
            raise AttributeError(
                'Rename attribute `parameter_name` to '
                '`field_name` for {}'.format(self.__class__)
            )
        self.parameter_name = '{}__id__exact'.format(self.field_name)
        super().__init__(request, params, model, model_admin)

        if self.rel_model:
            model = self.rel_model

        remote_field = model._meta.get_field(self.field_name).remote_field

        attrs = self.widget_attrs.copy()
       
        field = forms.ModelChoiceField(
            queryset=getattr(model, self.field_name).get_queryset(),
            widget=AutocompleteSelect(remote_field, model_admin.admin_site),
            required=False
        )

        self._add_media(model_admin)

        attrs['id'] = 'id-%s-dal-filter' % self.field_name
        
        if self.is_placeholder_title:
            attrs['data-placeholder'] = "By " + self.title
        
        self.rendered_widget = field.widget.render(
            name=self.parameter_name,
            value=self.used_parameters.get(self.parameter_name, ''),
            attrs=attrs
        )
    
    def _add_media(self, model_admin):
        if not hasattr(model_admin, 'Media'):
            raise Exception('Please add empty Media class to %s.' % model_admin)

        def _get_media(obj):
            return Media(media=getattr(obj, 'Media', None))

        media = _get_media(model_admin) + _get_media(AutocompleteFilter) + _get_media(self)

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