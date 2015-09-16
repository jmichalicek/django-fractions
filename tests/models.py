from django.db import models
from djfractions.models import DecimalFractionField

class TestModel(models.Model):
    """
    A test model to use for testing custom fields. This technique is based on core django code
    such as at https://github.com/django/django/blob/stable/1.8.x/tests/field_subclassing/models.py
    and https://github.com/django/django/blob/stable/1.8.x/tests/field_subclassing/tests.py
    although for now this model is just right in the test
    """
    data = DecimalFractionField()
