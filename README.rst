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

Then use it in a project::

    import djfractions

Features
--------

* Template tag for displaying float and Decimal values as fractions including mixed numbers


TODO
____

* Use unicode fractions instead of sub/sup when reasonable for output
* Consider not using sub/sup at all as they can be problematic for screen readers based on a very old discussion of this subject
* Tags and filters to convert to Decimal and/or float
* Test cases


Cookiecutter Tools Used in Making This Package
----------------------------------------------

*  cookiecutter
*  cookiecutter-djangopackage
