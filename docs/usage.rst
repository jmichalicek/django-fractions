========
Usage
========

Add ``djfractions`` to ``settings.INSTALLED_APPS``

Form Fields
-----------

DecimalFractionField
________________________________________

``DecimalFractionField(coerce_thirds=True, limit_denominator=None, use_mixed_numbers=True)``

Example::

    from django import forms
    from djfractions.forms import DecimalFractionField

    class MyForm(forms.Form):
        a_fraction = DecimalFractionField()


Template Tags
-------------

display_fraction
________________

``{% display_fraction value limit_denominator allow_mixed_numbers coerce_thirds %}``

The display_fraction tag displays a formatted fraction in an HTML template.  It takes
a value and optional parameters to limit the denominator, allow mixed numbers, and
adjust decimal/float values which usually are the result of rounding thirds back to
thirds based fractions.

The output of this tag can be changed by overriding the ``djfractions/display_fraction.html``
template.  This is because there are a number of style choices you might make depending
on needs.  In some cases <sup> and <sub> tags may cause issues with screen readers.  You
may just want to add css classes for easier styling.  The template context also includes
a ``unicode_entity`` value which has the html entity for the unicode value of a fraction
if one is available.  The unicode html entity is preferred by some people, but only a
small number of fractions are supported (particularly if you must support very old browsers)
and the styling is frequently difficult to match up exactly with <sup> and <sub> tags.::

    {% load fractions %}
    {% display_fraction 1.5 %}

Would output::

    1 <sup>1></sup>&frasl;<sub>1</sub>


The template context:

whole_number
    The whole number part of a fraction.  If ``allow_mixed_numbers`` is False then
    this will always be 0.

numerator
    The numerator of a fraction.  For values which are only a whole number the
    numerator will be 0.

denominator
    The denominator of a fraction.  For values which are only a whole number the
    denominator will be 1 for a fraction of 0/1.

unicode_entity
    The unicode_entity is the html entity for the unicode fraction if one exists.

allow_mixed_numbers
    The value passed to the tag for ``allow_mixed_numbers``.  Knowing this can be
    useful in template display logic.


The following unicode fraction HTML entities are supported by django-fractions.
They may not all be supported by your browser.

+----------+-------+------------+-----------+
| Entity   | IE 11 | Firefox 39 | Chrome 44 |
+==========+=======+============+===========+
| &frac12; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac13; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac23; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac14; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac34; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac15; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac25; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac35; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac45; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac16; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac56; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac17; | No    | No         | Yes       |
+----------+-------+------------+-----------+
| &frac18; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac38; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac58; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+
| &frac78; | Yes   | Yes        | Yes       |
+----------+-------+------------+-----------+


display_improper_fraction
_________________________

``{% display_improper_fraction value limit_denominator coerce_thirds %}``

The display_improper_fraction tag works the same as display_fraction with
its allow_mixed_numbers set to False.  It is just a shortcut for a common
use case.::

    {% load fractions %}
    {% display_improper_fraction 1.5 %}

Would output::

    <sup>3</sup>&frasl;<sub>2</sub>
