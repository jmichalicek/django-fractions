from django.db import models
from djfractions.models import DecimalFractionField

class TestModel(models.Model):
    """
    A test model to use for testing custom fields. This technique is based on core django code
    such as at https://github.com/django/django/blob/stable/1.8.x/tests/field_subclassing/models.py
    and https://github.com/django/django/blob/stable/1.8.x/tests/field_subclassing/tests.py
    although for now this model is just right in the test
    """
    defaults = DecimalFractionField(null=True, default=None)
    denominator_limited_to_ten = DecimalFractionField(
        limit_denominator=10, decimal_places=10, null=True, default=None)
    coerce_thirds_true = DecimalFractionField(
        coerce_thirds=True, decimal_places=10, null=True, default=None)
    # DecimalFractionField subclasses Django's FractionField
    # and that does some fiddling which when doing proper float division
    # will result in exceptions being raised if a fraction such as 1/3
    # is saved to the database.  Setting a max decimal_places fixes this.
    decimal_places_limited = DecimalFractionField(decimal_places=10,
                                                  coerce_thirds=False,
                                                  null=True,
                                                  default=None)
