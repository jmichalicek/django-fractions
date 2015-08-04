=============================
django-fractions
=============================

.. image:: https://badge.fury.io/py/django-fractions.png
    :target: https://badge.fury.io/py/django-fractions

.. image:: https://travis-ci.org/jmichalicek/django-fractions.png?branch=master
    :target: https://travis-ci.org/jmichalicek/django-fractions

Fraction display and form fields for Django

Documentation
-------------

The full documentation is at https://django-fractions.readthedocs.org.

Quickstart
----------

Install django-fractions::

    pip install django-fractions
    
Add ``djfractions`` to ``settings.INSTALLED_APPS``
    

Then use it in a project::

    import djfractions

In templates::

    {% load fractions %}
    {% display_fraction 1.25 %}

In Forms::

    from djfractions.forms import DecimalFractionField
    from django import forms

    class MyForm(froms.Form):
        a_fraction = DecimalFractionField()


Features
--------

* Template tag for displaying float and Decimal values as fractions including mixed numbers
* DecimalFractionField form field which handles input such as "1/4", "1 1/2", "1 and 1/2", and converts to a
  decimal.Decimal instance


TODO
____

* Read The Docs documentation
* Use unicode fractions instead of sub/sup when reasonable for output
* Consider not using sub/sup at all as they can be problematic for screen readers based on a very old discussion of this subject
* Possibly make the output of the template tags templated
* Tags and filters to convert to Decimal and/or float



Cookiecutter Tools Used in Making This Package
----------------------------------------------

*  cookiecutter
*  cookiecutter-djangopackage
