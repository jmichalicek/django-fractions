from __future__ import unicode_literals, absolute_import, division

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from decimal import Decimal
import fractions
import re

from . import quantity_to_decimal, is_number


class DecimalFractionField(forms.Field):
    """
    Displays and takes input as a fraction string such as 1/4 or 1 1/4
    but stores as a Decimal.
    """

    default_error_messages = {
        'invalid': _('Enter a fraction such as 1 1/4 or 1/4.'),
    }

    def __init__(self, *args, **kwargs):
        """
        :param bool coerce_thirds: Defaults to True.  If True
            then .3 repeating is forced to 1/3 rather than 3/10, 33/100, etc.
            and .66 and .67 are forced to 2/3.
        :param int limit_denominator: Set a maximum denominator to be used on
            fractions created from the field input.
        """
        self.coerce_thirds = kwargs.pop('coerce_thirds', True)
        self.limit_denominator = kwargs.pop('limit_denominator', None)
        super(DecimalFractionField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, Decimal) or isinstance(value, float):
            f = fractions.Fraction(value)
            dec = Decimal(value).quantize(Decimal('0.00'))

            if f.denominator == 1:
                return str(f)
            #elif dec == Decimal('.33') or dec == Decimal('.3') or dec == Decimal('.67') or dec == Decimal('.6'):
            #    f = f.limit_denominator(3)

            fraction_string = ''
            if f.numerator > f.denominator:
            # convert to complex number
                int_part = f.numerator // f.denominator
                f = fractions.Fraction(f.numerator - (int_part * f.denominator), f.denominator)
                fraction_string = u'%d' % int_part

            if self.limit_denominator:
                f = f.limit_denominator(self.limit_denominator)

            if self.coerce_thirds:
                temp_decimal = Decimal(f.numerator / f.denominator).quantize(Decimal('0.00'))
                if temp_decimal % 1 == Decimal('.33') or temp_decimal % 1 == Decimal('.3') \
                   or temp_decimal % 1 == Decimal('.67') or temp_decimal % 1 == Decimal('.6'):
                    f = f.limit_denominator(3)

            fraction_string = u'%s %d/%d' % (fraction_string, f.numerator, f.denominator)
        else:
            fraction_string = u'%s' % value
        return fraction_string.strip()

    def to_python(self, value):
        """
        Take string input such as 1/4 or 1 1/3 and convert to a :class:`decimal.Decimal`
        """
        if value in EMPTY_VALUES:
            return None

        if isinstance(value, Decimal) or isinstance(value, float) or isinstance(value, int):
            return Decimal(value)

        # some really lame validation that we do not have a string like "1 1 1/4" because that
        # is not a valid number.
        # these regexes should match fractions such as 1 1/4 and 1/4, with any number
        # of spaces between digits and / and any length of actual digits such as
        # 100 1/4 or 1 100/400, etc
        if not is_number(value) and not re.match(r'^\s*\d+\s*\/\s*\d+\s*$', value) \
           and not re.match(r'^\s*\d+(\s+|\s+and\s+|\s*\-\s*)\d+\s*\/\s*\d+$\s*', value):
            # this second matches optional whitespace, then a digit, then
            # whitespace OR the word 'and' with or without spaces OR a hyphen with
            # or without surrounding spaces, followed by another digit, a /, then a digit
            # examples: 1 1/2, 1-1/2, 1 - 1/2, 1 and 1/2, etc.
            raise ValidationError(self.error_messages['invalid'], code='invalid')

        try:
            value = quantity_to_decimal(value)
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value

    def validate(self, value):
        super(DecimalFractionField, self).validate(value)
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
