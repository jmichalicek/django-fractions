from django.db import models
from djfractions.models import DecimalFractionField


class TestModel(models.Model):
    """
    A test model to use for testing custom fields. This technique is based on core django code
    such as at https://github.com/django/django/blob/stable/1.8.x/tests/field_subclassing/models.py
    and https://github.com/django/django/blob/stable/1.8.x/tests/field_subclassing/tests.py
    although for now this model is just right in the test
    """

    defaults = DecimalFractionField(max_digits=10, decimal_places=5)
    denominator_limited_to_ten = DecimalFractionField(
        limit_denominator=10, decimal_places=10, max_digits=15, null=True, default=None
    )
    coerce_thirds_true = DecimalFractionField(
        coerce_thirds=True, decimal_places=10, max_digits=15, null=True, default=None
    )
    # DecimalFractionField Django's DecimalField in many aspects
    # and that does some fiddling which when doing proper float division
    # will result in exceptions being raised if a fraction such as 1/3
    # is saved to the database.  Setting a max decimal_places fixes this.
    decimal_places_limited = DecimalFractionField(
        decimal_places=10, max_digits=15, coerce_thirds=False, null=True, default=None
    )


class BadTestModel(models.Model):
    """
    A model with bad versions of the DecimalFractionField.

    This model is required for some of the field tests because some internals of
    Django expect that the field is part of a model and contribute_to_class() has been called
    and contribute_to_class() expects that a db migration which adds that field to the db
    has been run
    """

    missing_max_digits = DecimalFractionField(decimal_places=5)
    missing_decimal_places = DecimalFractionField(max_digits=5)
