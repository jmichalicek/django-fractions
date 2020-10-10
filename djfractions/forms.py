from django import forms
from django.core.exceptions import ValidationError
from django.core import validators
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from decimal import Decimal, InvalidOperation, DecimalException
import fractions
import numbers
import re

from . import quantity_to_decimal, is_number, get_fraction_parts, coerce_to_thirds, quantity_to_fraction


class FractionField(forms.Field):
    """
    Displays and takes input as a fraction string such as 1/4 or 1 1/4
    but returns a :class:`fractions.Fraction`.

    fraction = FractionField(coerce_thirds=True, limit_denominator=None,
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

    # matches standard 'x/y' fractions with 0 or more spaces before, after, or between characters.
    FRACTION_MATCH = re.compile(r'^\s*-?\s*\d+\s*\/\s*\d+\s*$')
    # matches mixed numbers such as '1 1/2' with any number of spaces and with common
    # separators of - (hyphen) and the word 'and' between the whole number and fraction part
    MIXED_NUMBER_MATCH = re.compile(r'^\s*-?\s*\d+(\s+|\s+and\s+|\s*\-\s*)\d+\s*\/\s*\d+\s*$')

    def __init__(
        self,
        max_value=None,
        min_value=None,
        limit_denominator=None,
        coerce_thirds=True,
        use_mixed_numbers=True,
        *args,
        **kwargs
    ):
        self.coerce_thirds = coerce_thirds
        self.limit_denominator = limit_denominator
        self.use_mixed_numbers = use_mixed_numbers
        self.max_value, self.min_value = max_value, min_value

        super().__init__(*args, **kwargs)
        if max_value is not None:
            self.validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(validators.MinValueValidator(min_value))

    def prepare_value(self, value):
        if value is None:
            return value

        try:
            whole_number, numerator, denominator = get_fraction_parts(
                value, self.use_mixed_numbers, self.limit_denominator, self.coerce_thirds
            )

            # if we are allowing mixed numbers (so non-fractional values,
            # including whole numbers) and numerator is falsey (should be 0)
            # just return the whole number.
            if (whole_number or whole_number == 0) and not numerator and self.use_mixed_numbers:
                return u'%s' % whole_number

            if whole_number and self.use_mixed_numbers:
                fraction_string = u'%d' % whole_number
            else:
                fraction_string = u''

            fraction_string = u'%s %d/%d' % (fraction_string, numerator, denominator)

        except (ValueError, InvalidOperation) as e:
            fraction_string = u'%s' % value

        return fraction_string.strip()

    def to_python(self, value):
        """
        Take string input such as 1/4 or 1 1/3 and convert to a :class:`fractions.Fraction`.
        This will also work with int, float, Decimal, and Fraction.
        """
        if value in validators.EMPTY_VALUES:
            return None

        if isinstance(value, str):
            # some really lame validation that we do not have a string like "1 1 1/4" because that
            # is not a valid number.
            # these regexes should match fractions such as 1 1/4 and 1/4, with any number
            # of spaces between digits and / and any length of actual digits such as
            # 100 1/4 or 1 100/400, etc
            if (
                not is_number(value)
                and not self.FRACTION_MATCH.match(value)
                and not self.MIXED_NUMBER_MATCH.match(value)
            ):
                # this second matches optional whitespace, then a digit, then
                # whitespace OR the word 'and' with or without spaces OR a hyphen with
                # or without surrounding spaces, followed by another digit, a /, then a digit
                # examples: 1 1/2, 1-1/2, 1 - 1/2, 1 and 1/2, etc.
                raise ValidationError(self.error_messages['invalid'], code='invalid')

            fraction = quantity_to_fraction(value)
        else:
            # it's not a string, so try to convert it to a Fraction
            # may need to catch some exceptions here and raise a ValidationError
            fraction = fractions.Fraction(value)

        if self.limit_denominator:
            fraction = fraction.limit_denominator(self.limit_denominator)

        if self.coerce_thirds and (not self.limit_denominator or self.limit_denominator > 3):
            fraction = coerce_to_thirds(fraction)

        return fraction


class DecimalFractionField(FractionField):
    """
    Displays and takes input as a fraction string such as 1/4 or 1 1/4
    but returns a :class:`decimal.Decimal`.

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
    :ivar max_value: The maximum value allowed
    :ivar min_value: The minimum value allowed

    :ivar int decimal_places: The maximum number of decimal places the
        resulting Decimal value may have
    :ivar int max_digits: The maximum number of digits, including decimal
        places, the resulting Decimal may have.
    """

    default_error_messages = {
        'invalid': _('Enter a fraction such as 1 1/4 or 1/4.'),
        'max_digits': ungettext_lazy(
            'Ensure that there are no more than %(max)s digit in total.',
            'Ensure that there are no more than %(max)s digits in total.',
            'max',
        ),
        'max_decimal_places': ungettext_lazy(
            'Ensure that there are no more than %(max)s decimal place.',
            'Ensure that there are no more than %(max)s decimal places.',
            'max',
        ),
        'max_whole_digits': ungettext_lazy(
            'Ensure that there are no more than %(max)s digit before the decimal point.',
            'Ensure that there are no more than %(max)s digits before the decimal point.',
            'max',
        ),
    }

    # def __init__(self, max_value=None, min_value=None, limit_denominator=None,
    #             coerce_thirds=True, use_mixed_numbers=True, *args, **kwargs):
    #    self.coerce_thirds = coerce_thirds
    #    self.limit_denominator = limit_denominator

    #    self.decimal_places = kwargs.get('decimal_places', None)
    #    self.max_digits = kwargs.get('max_digits', None)
    #    self.round_decimal = kwargs.get('round_decimal', False)
    #    super(DecimalFractionField, self).__init__(max_value=max_value, min_value=min_value,
    #            limit_denominator=limit_denominator, coerce_thirds=coerce_thirds,
    #            use_mixed_numbers=use_mixed_numbers, *args, **kwargs)

    def __init__(
        self,
        max_value=None,
        min_value=None,
        limit_denominator=None,
        coerce_thirds=True,
        use_mixed_numbers=True,
        *args,
        **kwargs
    ):
        self.use_mixed_numbers = use_mixed_numbers
        self.max_value, self.min_value = max_value, min_value

        self.decimal_places = kwargs.pop('decimal_places', None)
        self.max_digits = kwargs.pop('max_digits', None)
        self.round_decimal = kwargs.pop('round_decimal', False)

        super().__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Take string input such as 1/4 or 1 1/3 and convert to a :class:`decimal.Decimal`
        """
        if value in validators.EMPTY_VALUES:
            return None

        if isinstance(value, fractions.Fraction):
            return Decimal(value.numerator / value.denominator)

        # some really lame validation that we do not have a string like "1 1 1/4" because that
        # is not a valid number.
        # these regexes should match fractions such as 1 1/4 and 1/4, with any number
        # of spaces between digits and / and any length of actual digits such as
        # 100 1/4 or 1 100/400, etc
        if isinstance(value, str):
            if (
                not is_number(value)
                and not self.FRACTION_MATCH.match(value)
                and not self.MIXED_NUMBER_MATCH.match(value)
            ):
                # this second matches optional whitespace, then a digit, then
                # whitespace OR the word 'and' with or without spaces OR a hyphen with
                # or without surrounding spaces, followed by another digit, a /, then a digit
                # examples: 1 1/2, 1-1/2, 1 - 1/2, 1 and 1/2, etc.
                raise ValidationError(self.error_messages['invalid'], code='invalid')

            try:
                value = quantity_to_decimal(value)
            except DecimalException:
                raise ValidationError(self.error_messages['invalid'], code='invalid')
        else:
            value = Decimal(value)

        return value

    # def clean(self, value):
    #    if self.max_digits is not None and self.decimal_places is not None and self.round_decimal:
    #        value = self.round_decimal_value(value)
    #    return super(DecimalFractionField, self).clean(value)

    def round_decimal_value(self, value):
        # NOT SURE THIS IS A GOOD IDEA
        # This could muck with numbers in a way a user does not
        # expect due to the max_digits handling.  It might be better
        # to just have users handle rounding and digit manipulation
        # themselves in Form.clean_FOO()
        quantize_string = u'0' * self.decimal_places
        quantize_string = u'.%s' % quantize_string
        # round to max number of decimal places
        value = value.quantize(Decimal(quantize_string))
        sign, digittuple, exponent = value.as_tuple()
        digits, whole_digits, decimals = self._get_digit_counts(value)

        if digits <= self.max_digits:
            # total # digits is ok, but need to check if decimal places
            # need rounded
            if decimals > self.decimal_places:
                decimals_to_remove = self.decimal_places - decimals
            else:
                decimals_to_remove = 0
            allowed_decimals = decimals - decimals_to_remove
        elif whole_digits <= self.max_digits:
            # can we trim enough decimals to fit?
            allowed_decimals = self.max_digits - whole_digits
        else:
            allowed_decimals = decimals

        # this will give us '0' or '00', etc.
        quantize_string = u'0'
        if allowed_decimals > 0:
            quantize_string = quantize_string * allowed_decimals
            # if at least one decimal place, drop a decimal point in front.
            # if no decimal places can be used to reac max_digits then
            # use no leading decimal, causing Decimal.quantize() to round to
            # a whole number
            quantize_string = u'.%s' % quantize_string
        value = value.quantize(Decimal(quantize_string))
        return value

    def _get_digit_counts(self, value):
        """
        Returns tuple of (total_digits, whole_digits, decimals)
        """
        sign, digittuple, exponent = value.as_tuple()
        decimals = abs(exponent)
        digits = len(digittuple)
        if decimals > digits:
            digits = decimals
        whole_digits = digits - decimals
        return (digits, whole_digits, decimals)

    def validate(self, value):
        super().validate(value)
        if value in self.empty_values:
            return
        # Check for NaN, Inf and -Inf values. We can't compare directly for NaN,
        # since it is never equal to itself. However, NaN is the only value that
        # isn't equal to itself, so we can use this to identify NaN
        if value != value or value == Decimal("Inf") or value == Decimal("-Inf"):
            raise ValidationError(self.error_messages['invalid'], code='invalid')

        # max digits/decimal places validation.  Taken from django 1.8 forms.DecimalField
        # until this lib stops support django 1.8.  After that this can use
        # validators.DecimalValidator (added in django 1.9) added up in __init__()
        sign, digittuple, exponent = value.as_tuple()
        decimals = abs(exponent)
        # digittuple doesn't include any leading zeros.
        digits = len(digittuple)
        if decimals > digits:
            # We have leading zeros up to or past the decimal point.  Count
            # everything past the decimal point as a digit.  We do not count
            # 0 before the decimal point as a digit since that would mean
            # we would not allow max_digits = decimal_places.
            digits = decimals
        whole_digits = digits - decimals

        if self.max_digits is not None and digits > self.max_digits:
            raise ValidationError(
                self.error_messages['max_digits'], code='max_digits', params={'max': self.max_digits},
            )
        if self.decimal_places is not None and decimals > self.decimal_places:
            raise ValidationError(
                self.error_messages['max_decimal_places'],
                code='max_decimal_places',
                params={'max': self.decimal_places},
            )
        if (
            self.max_digits is not None
            and self.decimal_places is not None
            and whole_digits > (self.max_digits - self.decimal_places)
        ):
            raise ValidationError(
                self.error_messages['max_whole_digits'],
                code='max_whole_digits',
                params={'max': (self.max_digits - self.decimal_places)},
            )
        return value
