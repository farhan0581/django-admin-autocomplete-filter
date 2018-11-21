[![PyPI version](https://badge.fury.io/py/django-admin-autocomplete-filter.svg)](https://badge.fury.io/py/django-admin-autocomplete-filter)

Django Admin Autocomplete Filter
================================
A simple Django app to render list filters in django admin using autocomplete widget. This app is heavily inspired from [dal-admin-filters.](https://github.com/shamanu4/dal_admin_filters)

Overview:
---------

Django comes preshipped with an admin panel which is a great utility to create quick CRUD's.
The django 2.0 came with much needed [autocomplete_fields](https://docs.djangoproject.com/en/2.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.autocomplete_fields "autocomplete_fields") which uses select2 widget that comes with a search feature that loads the options asynchronously.
We can use this in django admin list filter.

    

Requirements:
-----------
Requires Django version >= 2.0

Installation:
------------
You can install it via pip or to get the latest version clone this repo.

`
pip install django-admin-autocomplete-filter
`

Add ``admin_auto_filters`` to your ``INSTALLED_APPS`` inside settings.py of your project.

Usage:
-----
Let's say we have following models:
``` python
class Artist(models.Model):
    name = models.CharField(max_length=128)

class Album(models.Model):
    name = models.CharField(max_length=64)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    cover = models.CharField(max_length=256, null=True, default=None)
```
And you would like to filter results in Album Admin on the basis of artist, then you can define `search fields` in Artist and then define filter as:

``` python
from admin_auto_filters.filters import AutocompleteFilter

class ArtistFilter(AutocompleteFilter):
    title = 'Artist' # display title
    field_name = 'artist' # name of the foreign key field

class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['name'] # this is required for django's autocomplete functionality
	...

class AlbumAdmin(admin.ModelAdmin):
    list_filter = [ArtistFilter]
    
    '''
       defining this class is required for AutocompleteFilter
       it's a bug and I am working on it.
    '''
    class Media:
        pass
	...
```

After following these steps you may see the filter as:

![](https://raw.githubusercontent.com/farhan0581/django-admin-autocomplete-filter/master/admin_auto_filters/media/screenshot1.png)

![](https://raw.githubusercontent.com/farhan0581/django-admin-autocomplete-filter/master/admin_auto_filters/media/screenshot2.png)

License:
--------
Django Admin Autocomplete Filter is an Open Source project licensed under the terms of the GNU GENERAL PUBLIC LICENSE.
