from __future__ import unicode_literals, absolute_import, division

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from decimal import Decimal, InvalidOperation
import fractions
import re

from . import quantity_to_decimal, is_number, get_fraction_parts


class DecimalFractionField(forms.Field):
    """
    Displays and takes input as a fraction string such as 1/4 or 1 1/4
    but stores as a Decimal.

    fraction = DecimalFractionField(coerce_thirds=True, limit_denominator=None,
                                    use_mixed_numbers=True)

    :ivar bool coerce_thirds: Defaults to True.  If True
        then .3 repeating is forced to 1/3 rather than 3/10, 33/100, etc.
        and .66 and .67 are forced to 2/3.
    :ivar int limit_denominator: Set a maximum denominator to be used on
        fractions created from the field input.
    :ivar bool use_mixed_numbers: If True initial values which are
        decimals and floats greater than 1 will be converted to a mixed
        number such as `1 1/2` in the form field's value.  If False then
        improper fractions such as `3/2` will be created. Defaults to True.
    """

    default_error_messages = {
        'invalid': _('Enter a fraction such as 1 1/4 or 1/4.'),
    }

    def __init__(self, *args, **kwargs):
        self.coerce_thirds = kwargs.pop('coerce_thirds', True)
        self.limit_denominator = kwargs.pop('limit_denominator', None)
        self.use_mixed_numbers = kwargs.pop('use_mixed_numbers', True)
        super(DecimalFractionField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        try:
            whole_number, numerator, denominator = get_fraction_parts(value,
                                                                      self.use_mixed_numbers,
                                                                      self.limit_denominator,
                                                                      self.coerce_thirds)

            # if we are allowing mixed numbers (so non-fractional values,
            # including whole numbers) and numerator is falsey (should be 0)
            # just return the whole number.
            if (whole_number or whole_number == 0) and not numerator \
               and self.use_mixed_numbers:
                return u'%s' % whole_number

            if whole_number and self.use_mixed_numbers:
                fraction_string = u'%d' % whole_number
            else:
                fraction_string = u''

            fraction_string = u'%s %d/%d' % \
                              (fraction_string, numerator, denominator)

        except (ValueError, InvalidOperation) as e:
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
