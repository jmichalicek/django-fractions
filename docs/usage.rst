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
thirds based fractions.::

    {% load fractions %}
    {% display_fraction 1.25 %}
    
Would output::

    1 <sup>1></sup>&frasl;<sub>4</sub>
