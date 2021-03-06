"""Defines autocomplete filters and helper functions for the admin."""

from django.contrib.admin import SimpleListFilter
from django.contrib.admin.utils import prepare_lookup_value
from django.contrib.admin.widgets import (
    AutocompleteSelect as BaseAutocompleteSelect,
    AutocompleteSelectMultiple as BaseAutocompleteSelectMultiple,
)
from django.db.models import ForeignObjectRel
from django.db.models.constants import LOOKUP_SEP  # this is '__'
from django.db.models.fields.related_descriptors import (
    ReverseManyToOneDescriptor, ManyToManyDescriptor,
)
from django.forms import ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import Media, MEDIA_TYPES, media_property
from django.shortcuts import reverse


class AutocompleteSelect(BaseAutocompleteSelect):
    """A customize AutocompleteSelect that allows a custom URL."""

    def __init__(self, rel, admin_site, attrs=None, choices=(), using=None, custom_url=None):
        self.custom_url = custom_url
        super().__init__(rel, admin_site, attrs, choices, using)
    
    def get_url(self):
        return self.custom_url if self.custom_url else super().get_url()


class AutocompleteSelectMultiple(BaseAutocompleteSelectMultiple):
    """A customize AutocompleteSelectMultiple that allows a custom URL."""

    def __init__(self, rel, admin_site, attrs=None, choices=(), using=None, custom_url=None):
        self.custom_url = custom_url
        super().__init__(rel, admin_site, attrs, choices, using)

    def get_url(self):
        return self.custom_url if self.custom_url else super().get_url()


class AutocompleteFilter(SimpleListFilter):
    template = 'django-admin-autocomplete-filter/autocomplete-filter.html'
    title = ''
    field_name = ''
    field_pk = 'pk'
    use_pk_exact = True
    is_placeholder_title = False
    widget_attrs = {}
    rel_model = None
    parameter_name = None
    form_field = None
    form_widget = None
    multi_select = False

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'django-admin-autocomplete-filter/js/autocomplete_filter_qs.js',
        )
        css = {
            'screen': (
                'django-admin-autocomplete-filter/css/autocomplete-fix.css',
            ),
        }

    def __init__(self, request, params, model, model_admin):
        self.set_parameter_name(request, model_admin)
        super().__init__(request, params, model, model_admin)

        # Instance vars not used, to make argument passing explicit
        model_used = self.rel_model if self.rel_model else model
        remote_field = model_used._meta.get_field(self.field_name).remote_field
        widget = self.get_widget(request, model_admin, remote_field)
        field = self.get_field(request, model_admin, model_used, widget)
        self._add_media(model_admin, widget)
        attrs = self.get_attrs(request, model_admin)
        self.rendered_widget = self.render_widget(field, attrs)

    @staticmethod
    def _get_rel_model_for_filter(model, parameter_name):
        """A method to facilitate overriding."""
        return _get_rel_model(model, parameter_name)

    @classmethod
    def generate_choice_field(cls, label_item, form_field, request, model_admin):
        """
        Create a ModelChoiceField variant with a modified label_from_instance.
        May be a ModelMultipleChoiceField if multi-select is enabled, or other custom class.
        Note that label_item can be a callable, or a model field, or a model callable.
        """

        class LabelledModelChoiceField(form_field):
            def label_from_instance(self, obj):
                if callable(label_item):
                    value = label_item(obj)
                elif hasattr(obj, str(label_item)):
                    attr = getattr(obj, label_item)
                    if callable(attr):
                        value = attr()
                    else:
                        value = attr
                else:
                    raise ValueError('Invalid label_item specified: %s' % str(label_item))
                return value

        return LabelledModelChoiceField

    def get_attrs(self, request, model_admin):
        """Gather the HTML tag attrs from all sources."""
        attrs = self.widget_attrs.copy()
        attrs['id'] = 'id-%s-daaf-filter' % self.parameter_name
        if self.is_placeholder_title:
            # Upper case letter P as dirty hack for bypass django2 widget force placeholder value as empty string ("")
            attrs['data-Placeholder'] = self.title
        return attrs

    @staticmethod
    def get_queryset_for_field(model, name):
        """Determine the appropriate queryset for the filter itself."""
        try:
            field_desc = getattr(model, name)
        except AttributeError:
            field_desc = model._meta.get_field(name)
        if isinstance(field_desc, ManyToManyDescriptor):
            related_model = field_desc.rel.related_model if field_desc.reverse else field_desc.rel.model
        elif isinstance(field_desc, ReverseManyToOneDescriptor):
            related_model = field_desc.rel.related_model  # look at field_desc.related_manager_cls()?
        elif isinstance(field_desc, ForeignObjectRel):
            # includes ManyToOneRel, ManyToManyRel
            # also includes OneToOneRel - not sure how this would be used
            related_model = field_desc.related_model
        else:
            # primarily for ForeignKey/ForeignKeyDeferredAttribute
            # also includes ForwardManyToOneDescriptor, ForwardOneToOneDescriptor, ReverseOneToOneDescriptor
            return field_desc.get_queryset()
        return related_model.objects.get_queryset()

    def get_form_widget(self, request, model_admin):
        """Determine the form widget class to be used."""
        if self.form_widget is not None:
            return self.form_widget
        elif self.multi_select:
            return AutocompleteSelectMultiple
        else:
            return AutocompleteSelect

    def get_widget(self, request, model_admin, remote_field):
        """Create the form widget to be used."""
        widget_class = self.get_form_widget(request, model_admin)
        return widget_class(
            remote_field,
            model_admin.admin_site,
            custom_url=self.get_autocomplete_url(request, model_admin),
        )

    def get_form_field(self, request, model_admin):
        """Determine the form field class to be used."""
        if self.form_field is not None:
            return self.form_field
        elif self.multi_select:
            return ModelMultipleChoiceField
        else:
            return ModelChoiceField

    def get_field(self, request, model_admin, model, widget):
        """Create the form field to be used."""
        form_field_class = self.get_form_field(request, model_admin)
        return form_field_class(
            queryset=self.get_queryset_for_field(model, self.field_name),
            widget=widget,
            required=False,
        )

    def _add_media(self, model_admin, widget):
        """Update the relevant ModelAdmin Media class, creating it if needed."""

        if not hasattr(model_admin, 'Media'):
            model_admin.__class__.Media = type('Media', (object,), dict())
            model_admin.__class__.media = media_property(model_admin.__class__)

        def _get_media(obj):
            return Media(media=getattr(obj, 'Media', None))

        media = _get_media(model_admin) + widget.media + _get_media(AutocompleteFilter) + _get_media(self)

        for name in MEDIA_TYPES:
            setattr(model_admin.Media, name, getattr(media, '_' + name))

    def has_output(self):
        """Indicate that some choices will be output for this filter."""
        return True

    def lookups(self, request, model_admin):
        """Values for rendering. Not used by Select2 widget."""
        return ()

    def prepare_value(self):
        """Prepare the input string value for use."""
        params = self.used_parameters.get(self.parameter_name, '')
        return prepare_lookup_value(self.parameter_name, params)

    def queryset(self, request, queryset):
        """
        Apply filter to the queryset. Note that distinct() is NOT automatically
        applied, which may result in duplicate values unless applied elsewhere.
        """
        value = self.value()
        if value:
            prepared_value = prepare_lookup_value(self.parameter_name, value)
            return queryset.filter(**{self.parameter_name: prepared_value})
        else:
            return queryset

    def render_widget(self, field, attrs):
        """Render the widget."""
        prepared_value = self.prepare_value()
        # FIXME check that value is okay before using, make e=1 if not?
        return field.widget.render(
            name=self.parameter_name,
            value=prepared_value,
            attrs=attrs
        )

    def set_parameter_name(self, request, model_admin):
        """Set the value of self.parameter_name based on class variables."""
        if self.parameter_name is None:
            if self.multi_select:
                if self.use_pk_exact:  # note that "exact" is a misnomer here
                    self.parameter_name += '__{}__in'.format(self.field_pk)
                else:
                    self.parameter_name += '__in'.format(self.field_pk)
            else:
                if self.use_pk_exact:
                    self.parameter_name += '__{}__exact'.format(self.field_pk)
                else:
                    self.parameter_name = self.field_name

    def get_autocomplete_url(self, request, model_admin):
        """
        Hook to specify your custom view for autocomplete,
        instead of default django admin's search_results.
        """
        return None


def _get_rel_model(model, parameter_name):
    """
    A way to calculate the model for a parameter_name that includes LOOKUP_SEP.
    """
    field_names = str(parameter_name).split(LOOKUP_SEP)
    if len(field_names) == 1:
        return None
    else:
        rel_model = model
        for name in field_names[:-1]:
            rel_model = rel_model._meta.get_field(name).related_model
        return rel_model


def AutocompleteFilterFactory(
        title, base_parameter_name,
        viewname='', use_pk_exact=False, label_by=str, multi_select=False,
):
    """
    An autocomplete widget filter with a customizable title. Use like this:
        AutocompleteFilterFactory('My title', 'field_name')
        AutocompleteFilterFactory('My title', 'fourth__third__second__first')
    Be sure to include distinct in the model admin get_queryset() if the second form is used.
    Assumes: parameter_name == f'fourth__third__second__{field_name}'
        * title: The title for the filter.
        * base_parameter_name: The field to use for the filter.
        * viewname: The name of the custom AutocompleteJsonView URL to use, if any.
        * use_pk_exact: Whether to use '__pk__exact' in the parameter name when possible.
        * label_by: How to generate the static label for the widget - a callable, the name
          of a model callable, or the name of a model field.
        * multi_select: Whether the filter should allow multiple selections, which if true
          may require manual use of queryset.distinct() to remove duplicates.
    """

    class NewMetaFilter(type(AutocompleteFilter)):
        """A metaclass for an autogenerated autocomplete filter class."""

        def __new__(cls, name, bases, attrs):
            super_new = super().__new__(cls, name, bases, attrs)
            super_new.use_pk_exact = use_pk_exact
            field_names = str(base_parameter_name).split(LOOKUP_SEP)
            super_new.field_name = field_names[-1]
            super_new.parameter_name = base_parameter_name
            if len(field_names) <= 1 and super_new.use_pk_exact:
                super_new.parameter_name += '__{}__exact'.format(super_new.field_pk)
            return super_new

    class NewFilter(AutocompleteFilter, metaclass=NewMetaFilter):
        """An autogenerated autocomplete filter class."""

        def __init__(self, request, params, model, model_admin):
            self.rel_model = self._get_rel_model_for_filter(model, base_parameter_name)
            form_field = self.get_form_field(request, model_admin)
            self.form_field = self.generate_choice_field(label_by, form_field, request, model_admin)
            super().__init__(request, params, model, model_admin)
            self.title = title
            self.multi_select = multi_select

        def get_autocomplete_url(self, request, model_admin):
            if viewname == '':
                return super().get_autocomplete_url(request, model_admin)
            else:
                return reverse(viewname)

    return NewFilter
