# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import, print_function
import django
if django.VERSION[0] < 3:
	from django.utils import six
	SIX_OR_STR = six.string_types
else:
	SIX_OR_STR = str

from django.core import checks
from django.db import connection
from django.db.models import DecimalField, Field
from django.utils.translation import ugettext_lazy as _

import decimal
import fractions
import logging

from .. import coerce_to_thirds
from .. import forms as fraction_forms


logger = logging.getLogger(__name__)


class DecimalFractionField(Field):
    """
    Field which stores values as a Decimal value, but uses
    :class:`fractions.Fraction` for its value
    """
    empty_strings_allowed = False
    default_error_messages = {
        'invalid': _("'%(value)s' value must be a fraction number."),
    }
    description = _("Fraction number stored in the database as a Decimal")

    def __init__(self, verbose_name=None, name=None, max_digits=None, blank=False, null=False,
                 decimal_places=None, limit_denominator=None, coerce_thirds=True,
                 **kwargs):
        self.limit_denominator = limit_denominator
        self.coerce_thirds = coerce_thirds

        # for decimal stuff
        self.max_digits, self.decimal_places, self.blank, self.null = max_digits, decimal_places, blank, null

        super(DecimalFractionField, self).__init__(verbose_name=verbose_name,
                                                   name=name,
                                                   blank=blank,
                                                   null=null,
                                                   **kwargs)

    def check(self, **kwargs):
        errors = super(DecimalFractionField, self).check(**kwargs)

        digits_errors = self._check_decimal_places()
        digits_errors.extend(self._check_max_digits())
        if not digits_errors:
            errors.extend(self._check_decimal_places_and_max_digits(**kwargs))
        else:
            errors.extend(digits_errors)
        return errors

    def _check_decimal_places(self):
        try:
            decimal_places = int(self.decimal_places)
            if decimal_places < 0:
                raise ValueError()
        except TypeError:
            return [
                checks.Error(
                    "DecimalFractionFields must define a 'decimal_places' attribute.",
                    obj=self,
                    id='fields.E130',
                )
            ]
        except ValueError:
            return [
                checks.Error(
                    "'decimal_places' must be a non-negative integer.",
                    obj=self,
                    id='fields.E131',
                )
            ]
        else:
            return []

    def _check_max_digits(self):
        try:
            max_digits = int(self.max_digits)
            if max_digits <= 0:
                raise ValueError()
        except TypeError:
            return [
                checks.Error(
                    "DecimalFractionFields must define a 'max_digits' attribute.",
                    obj=self,
                    id='fields.E132',
                )
            ]
        except ValueError:
            return [
                checks.Error(
                    "'max_digits' must be a positive integer.",
                    obj=self,
                    id='fields.E133',
                )
            ]
        else:
            return []

    def _check_decimal_places_and_max_digits(self, **kwargs):
        if int(self.decimal_places) > int(self.max_digits):
            return [
                checks.Error(
                    "'max_digits' must be greater or equal to 'decimal_places'.",
                    obj=self,
                    id='fields.E134',
                )
            ]
        return []

	# If running pre-django 3.0 use context, depricated in 3.0
    if django.VERSION[0] < 3:
        def from_db_value(self, value, expression, connection, context):
            if value is None:
                return value

            # this probably needs to call to_fraction()
            # cann it just call to_python() for now?
            #return fractions.Fraction(value)
            return self.to_python(value)
    else:
        def from_db_value(self, value, expression, connection):
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

    def to_python(self, value):
        if value is None:
            return value

        # probably need similar error handling to
        # https://github.com/django/django/blob/stable/1.8.x/django/db/models/fields/__init__.py#L1598
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

    def deconstruct(self):
        name, path, args, kwargs = super(DecimalFractionField, self).deconstruct()
        kwargs['limit_denominator'] = self.limit_denominator
        kwargs['coerce_thirds'] = self.coerce_thirds

        # added this
        # copied from decimal field
        if self.max_digits is not None:
            kwargs['max_digits'] = self.max_digits
        if self.decimal_places is not None:
            kwargs['decimal_places'] = self.decimal_places

        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults ={
            'form_class': fraction_forms.FractionField
        }
        defaults.update(kwargs)
        return super(DecimalFractionField, self).formfield(**defaults)

    def get_internal_type(self):
        # returning DecimalField, since we use the same backing column type as that
        # and this is safer than overriding db_type() and db_check() since that would
        # require maintaining the mapping for every db adapter.
        return "DecimalField"

    def _format(self, value):
        if isinstance(value, SIX_OR_STR):
            return value
        else:
            return self.format_number(value)

    def format_number(self, value):
        """
        Formats a number into a string with the requisite number of digits and
        decimal places.
        """
        # Method moved to django.db.backends.utils.
        #
        # It is preserved because it is used by the oracle backend
        # (django.db.backends.oracle.query), and also for
        # backwards-compatibility with any external code which may have used
        # this method.
        from django.db.backends import utils
        return utils.format_number(value, self.max_digits, self.decimal_places)

