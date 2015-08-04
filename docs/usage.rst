========
Usage
========

Add ``djfractions`` to ``settings.INSTALLED_APPS``

To use django-fractions in a project::

    from django import forms
    from djfractions.forms import DecimalFractionField
    
    class MyForm(forms.Form):
        a_fraction = DecimalFractionField()
        
To use it in a template::

    {% load fractions %}
    {% display_fraction 1.25 %}
