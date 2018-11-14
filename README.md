
Django Inspectdb Refactor
========================
A simple Django app to render list filters in django admin using autocomplete widget.

Overview:
---------

Django's ``inspectb`` command prepares database models classes based on existing database.
    This is very handy tool, in case we have to work on some already existing database.
    
   It outputs the classes to standard output, which can be pipelined to a python file.
    
 But when you have a large database, containing hundreds of tables, the models file becomes too large. It is better to write ``separate model file for each table`` and keep that under models folder inside the app directory. Django will get the model classes from the ``init`` file you write inside the models folder.
 Same holds for admin, views and forms.
    
 Django Inspectdb Refactor will automatically create the required folders and create separate python files for each model.
    

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
dfdf
 

License:
--------
Django Inspectdb Refactor is an Open Source project licensed under the terms of the GNU GENERAL PUBLIC LICENSE.
