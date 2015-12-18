# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, absolute_import, print_function

from django.db import connection
from django.db.models import DecimalField
from django.utils.translation import ugettext_lazy as _

import decimal
import fractions
import logging

from . import coerce_to_thirds


logger = logging.getLogger(__name__)

class DecimalFractionField(DecimalField):
    """
    Field which stores values as a Decimal value, but uses
    :class:`fractions.Fraction` for its value
    """
    default_error_messages = {
        'invalid': _("'%(value)s' value must be a fraction number."),
    }
    description = _("Fraction number")

    def __init__(self, verbose_name=None, name=None, max_digits=None,
                 decimal_places=None, limit_denominator=None, coerce_thirds=True,
                 **kwargs):
        self.limit_denominator = limit_denominator
        self.coerce_thirds = coerce_thirds

        super(DecimalFractionField, self).__init__(verbose_name=verbose_name,
                                                   name=name,
                                                   max_digits=max_digits,
                                                   decimal_places=decimal_places,
                                                   **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value

        # this probably needs to call to_fraction()
        # cann it just call to_python() for now?
        #return fractions.Fraction(value)
        return self.to_python(value)

    def get_db_prep_save(self, value, connection):
        # for django 1.9 the following will need used.
        if hasattr(connection.ops, 'adapt_decimalfield_value'):
            return connection.ops.adapt_decimalfield_value(self.get_prep_value(value),
                                                           self.max_digits, self.decimal_places)
        else:
            return connection.ops.value_to_db_decimal(self.get_prep_value(value),
                                                      self.max_digits, self.decimal_places)
        #v = float(value)
        #return self.get_db_prep_value(value, connection, prepared=False)
        #return super(DecimalFractionField, self).get_db_prep_save(value=v, connection=connection)


    def to_python(self, value):
        if value is None:
            return value

        # probably need similar error handling to
        # https://github.com/django/django/blob/stable/1.8.x/django/db/models/fields/__init__.py#L1598
        # Also probably need to actually call to_fraction(value) here
        #return fractions.Fraction(value)
        return self.to_fraction(value)

    def get_prep_value(self, value):
        # not super clear, docs sound like this must be overridden and is the
        # reverse of to_python, but
        # django.db.models.fields.DecimalField just calls self.to_python() here
        # TODO:
        # see https://docs.djangoproject.com/en/1.8/howto/custom-model-fields/#converting-python-objects-to-query-values
        # for usage.
        if value is None:
            return value

        if isinstance(value, fractions.Fraction):
            value = float(value)
        return decimal.Decimal(value)

    def to_fraction(self, value):
        fraction_value = fractions.Fraction(value)
        if self.limit_denominator:
            fraction_value = fraction_value.limit_denominator(self.limit_denominator)

        if self.coerce_thirds and (not self.limit_denominator or self.limit_denominator > 3):
            fraction_value = coerce_to_thirds(fraction_value)

        return fraction_value

    #def value_to_string(self, obj):
    #    pass

    # probably need to override deconstruct()
    # probably need to override from_db_value() to return a fraction
