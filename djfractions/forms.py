from __future__ import unicode_literals, absolute_import

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from decimal import Decimal
import fractions
import re

from . import quantity_to_decimal


class DecimalFractionField(forms.Field):
    """
    Displays and takes input as a fraction string such as 1/4 or 1 1/4
    but stores as a Decimal.

    This may be updated to handle float, allow specifying the
    decimal params, etc.
    """

    default_error_messages = {
        'invalid': _('Enter a fraction such as 1 1/4 or 1/4.'),
    }

    def __init__(self, *args, **kwargs):
        """
        Takes optional param `coerce_thirds`, which defaults to True.  If True
        then .3 repeating is forced to 1/3 rather than 3/10, 33/100, etc.
        and .66 and .67 are forced to 2/3.
        """
        self.coerce_thirds = kwargs.pop('coerce_thirds', True)
        super(FractionField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, Decimal):
            f = fractions.Fraction(value)
            dec = Decimal(value).quantize(Decimal('0.00'))

            if f.denominator == 1:
                return str(f)
            elif dec == Decimal('.33') or dec == Decimal('.3') or dec == Decimal('.67') or dec == Decimal('.6'):
                f = f.limit_denominator(3)

            fraction_string = ''
            if f.numerator > f.denominator:
            # convert to complex number
                int_part = f.numerator // f.denominator
                f = fractions.Fraction(f.numerator - (int_part * f.denominator), f.denominator)
                fraction_string = u'%d' % int_part

            gcd = fractions.gcd(f.numerator, f.denominator)
            # reduce to lowest terms
            f = f/gcd

            if self.coerce_thirds:
                temp_decimal = Decimal(f.numerator / f.denominator).quantize(Decimal('0.00'))
                if temp_decimal == Decimal('.33') or temp_decimal == Decimal('.3') or \
                   temp_decimal == Decimal('.67') or temp_decimal == Decimal('.6'):
                    f = f.limit_denominator(3)

            fraction_string = '%s %d/%d' % (fraction_string, f.numerator, f.denominator)
        else:
            fraction_string = value
        return fraction_string.strip()

    def to_python(self, value):
        """
        Take string input such as 1/4 or 1 1/3 and convert to a :class:`decimal.Decimal`
        """
        # if this works, I should move quantity_to_decimal into the core app
        from recipes import quantity_to_decimal

        if value in EMPTY_VALUES:
            return None

        if isinstance(value, Decimal):
            return value

        # some really lame validation that we do not have a string like "1 1 1/4" because that
        # is not a valid number.
        # these regexes should match 1 1/4 and 1/4, with any number of spaces between digits and /
        # and any length of actual digits such as 100 1/4 or 1 100/400, etc
        try:
            int(value)
            is_int = True
        except ValueError:
            is_int = False
        if not is_int and not re.match(r'^\s*\d+\s*\/\s*\d+\s*$', value) and not re.match(r'^\s*\d+\s+\d+\s*\/\s*\d+$\s*', value):
            raise ValidationError(self.error_messages['invalid'], code='invalid')

        try:
            value = quantity_to_decimal(value)
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value

    def validate(self, value):
        super(FractionField, self).validate(value)
        if value in self.empty_values:
            return
        # Check for NaN, Inf and -Inf values. We can't compare directly for NaN,
        # since it is never equal to itself. However, NaN is the only value that
        # isn't equal to itself, so we can use this to identify NaN
        if value != value or value == Decimal("Inf") or value == Decimal("-Inf"):
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        sign, digittuple, exponent = value.as_tuple()
        decimals = abs(exponent)
        # digittuple doesn't include any leading zeros.
        digits = len(digittuple)

        return value
