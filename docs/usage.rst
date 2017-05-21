========
Usage
========

Add ``djfractions`` to ``settings.INSTALLED_APPS``

Model Fields
------------

DecimalFractionField
--------------------

.. code-block:: python

    djfractions.models.DecimalFractionField(verbose_name=None,
                                            name=None,
                                            max_digits=None,
                                            decimal_places=None,
                                            limit_denominator=None,
                                            coerce_thirds=True,
                                            **kwargs)

Takes a :class:`fractions.Fraction` value, stores it as a decimal value,
and then returns it as a :class:`fractions.Fraction`. This field is highly
based on Django's :class:`models.DecimalField` implementation and so
the `max_digits` and `decimal_places` arguments are required.

:param str verbose_name: The verbose name of the field
:param str name: Name of the field
:param int max_digits: Maximum number of digits to use for the Decimal representation
:param int decimal_places: Maximum number of decimal places to use for the Decimal representation
:param int limit_denominator:  Limits the fraction's denominator to this value if it is set.
:paraam bool coerce_thirds: If True, then when values which appear to be Decimal values which started as 1/3 or 2/3 will be forced back to 1/3 or 2/3 when retrieved from the database.

Form Fields
-----------

FractionField
________________________________________

.. code-block:: python

    FractionField(max_value=None,
                  min_value=None,
                  coerce_thirds=True,
                  limit_denominator=None,
                  use_mixed_numbers=True)

Returns a :class:`fractions.Fraction` instance.  Takes a string formatted
as a fraction such as 1/4, 1 1/4, 1-1/4, 1 and 1/4, or -1/4 as input in a form.

Example::

  from django import forms
  from djfractions.forms import FractionField

  class MyForm(forms.Form):
      a_fraction = FractionField()

:param Decimal max_value: The maximum value allowed for this field
:param Decimal min_value: The minimum value allowed for this field
:param int limit_denominator:  Limits the fraction's denominator to this value if it is set.
:param bool coerce_thirds: If True, then when values which appear to be Decimal values which started as 1/3 or 2/3 will be forced back to 1/3 or 2/3 when retrieved from the database.
:param bool use_mixed_numbers: If True initial values which are decimals and floats greater than 1 will be converted to a mixed number such as `1 1/2` in the form field's value.  If False then improper fractions such as `3/2` will be created. Defaults to True. 

DecimalFractionField
________________________________________

.. code-block:: python

    DecimalFractionField(max_value=None,
                         min_value=None,
                         coerce_thirds=True,
                         limit_denominator=None,
                         use_mixed_numbers=True,
                         max_digits=None,
                         decimal_places=None)

Returns a :class:`decimal.Decimal` instance.  Takes a string formatted
as a fraction such as 1/4, 1 1/4, 1-1/4, 1 and 1/4, or -1/4 as input in a form.

:param bool coerce_thirds: Defaults to True.  If True then .3 repeating is forced to 1/3 rather than 3/10, 33/100, etc. and .66 and .67 are forced to 2/3.
:param int limit_denominator: Set a maximum denominator to be used on fractions created from the field input.
:param bool use_mixed_numbers: If True initial values which are decimals and floats greater than 1 will be converted to a mixed number such as `1 1/2` in the form field's value.  If False then improper fractions such as `3/2` will be created. Defaults to True.
:param max_value: The maximum value allowed
:param min_value: The minimum value allowed
:param int decimal_places: The maximum number of decimal places the resulting Decimal value may have
:param int max_digits: The maximum number of digits, including decimal places, the resulting Decimal may have.


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

    1 <sup>1</sup>&frasl;<sub>2</sub>


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
