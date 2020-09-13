__version__ = '2.0.0'

from decimal import Decimal
import fractions
import re


__all__ = [
    'quantity_to_decimal',
    'is_number',
    'is_fraction',
    'get_fraction_parts',
    'get_fraction_unicode_entity',
]

HTML_ENTITIES = [
    '&frac12;',
    '&frac13;',
    '&frac23;',
    '&frac14;',
    '&frac34;',
    '&frac15;',
    '&frac25;',
    '&frac35;',
    '&frac45;',
    '&frac16;',
    '&frac56;',
    '&frac17;',
    '&frac18;',
    '&frac38;',
    '&frac58;',
    '&frac78;',
]


def is_number(s):
    """
    Determine if the input value is numeric - an int, float, decimal.Decimal,
    or a string such as '1', '1.23', etc.

    :param s: A string value to check to see if it represents a float or int.
    """
    try:
        int(s)
        return True
    except ValueError:
        pass

    try:
        float(s)
        return True
    except ValueError:
        pass

    return False


def is_fraction(s):
    """
    Determine if the input string appears to represent a fraction.
    This does not include mixed numbers such as 1 1/3

    :param s: A string value to check if it is formatted as a fraction.
    """
    return bool(re.match(r'^-?\d+/\d+$', s))


def coerce_to_thirds(value):
    """
    takes a :class:`fractions.Fraction` and forces it to thirds if it is one that
    is frequently the result of taking a number such as 1/3, converting to decimal/float,
    then back to a fraction.
    """
    temp_decimal = Decimal(value.numerator / value.denominator).quantize(Decimal('0.00'))
    if (
        temp_decimal % 1 == Decimal('.33')
        or temp_decimal % 1 == Decimal('.3')
        or temp_decimal % 1 == Decimal('.67')
        or temp_decimal % 1 == Decimal('.6')
    ):
        value = value.limit_denominator(3)
    return value


def quantity_to_decimal(quantity_string):
    """
    Take a quantity string and return a decimal.

    Handles one hundred, two hundred, three hundred twenty five,
    1, 1 1/4, 1 and 1/4, 1.25, .25.  Negative values should have
    the negative sign first, such as -1/4 or -1 1/4

    :param quantity_string: String to convert to a :class:`decimal.Decimal`
    """

    # get actual fraction-like strings to be N/N with no spaces
    quantity_string = quantity_string.strip()
    quantity_string = re.sub(r'\s*/\s*', '/', quantity_string)

    if is_number(quantity_string):
        return Decimal(quantity_string)

    if is_fraction(quantity_string):
        return _fraction_string_to_decimal(quantity_string)

    # assume the a hyphen between a whole value and fraction such as 1-1/4
    # is a separator and not a negative fraction.
    # If the negative is first though, then we need to keep it negative.
    positive_or_negative = -1 if quantity_string.startswith('-') else 1
    quantity_string = quantity_string.replace('-', ' ')

    parts = quantity_string.split()
    parts_length = len(parts)

    # it must be a mixed number like 1 1/4
    number_stack = []  # for storing the entire number to return in parts
    for part in parts:
        if is_fraction(part):
            number_stack.append(_fraction_string_to_decimal(part))
        elif is_number(part):
            number_stack.append(Decimal(part))

    return Decimal(sum(number_stack)) * positive_or_negative


def quantity_to_fraction(quantity_string):
    """
    Take a quantity string and return a :class:`fractions.Fraction`.

    Handles one hundred, two hundred, three hundred twenty five,
    1, 1 1/4, 1 and 1/4, 1-1/4, 1.25, .25. Negative values should have
    the negative sign first, such as -1/4 or -1 1/4

    :param quantity_string: String to convert to a :class:`fractions.Fraction`
    """
    # get actual fraction-like strings to be N/N with no spaces
    quantity_string = quantity_string.strip()
    quantity_string = re.sub(r'\s*/\s*', '/', quantity_string)
    if is_number(quantity_string):
        return fractions.Fraction(quantity_string)

    if is_fraction(quantity_string):
        return _fraction_string_to_fraction(quantity_string)

    # it must be a something like 1 1/4
    # assume that a hyphen between a whole value and fraction such as 1-1/4
    # is a separator and not a negative fraction.
    # If the negative is first though, then we need to keep it negative.
    # Cannot just keep the fraction on the int or we end up subtraction.
    # -1 1/4 becomes -3/4 when what is meant is -5/4
    positive_or_negative = -1 if quantity_string.startswith('-') else 1

    # non-capturing group in the middle handls just a space, hyphen with
    # optional spaces, or the word and.  Examples:
    # 1 1/4, 1-1/4, 1 - 1/4, 1 and 1/4
    parts = re.match(r'^-?(\d+)(?:\s+|\s*-?\s*|\s+and\s+)(\d+\/\d+)', quantity_string)
    # parts.group(0) is the entire string, 1 is the whole number bit
    f = fractions.Fraction(parts.group(2))
    f = (f + int(parts.group(1))) * positive_or_negative
    return f


def _fraction_string_to_fraction(fraction):
    """
    Convert a string representing a fraction to a :class:`fractions.Fraction`
    """
    parts = fraction.split('/')
    numerator = int(parts[0])
    denominator = int(parts[1])
    return fractions.Fraction(numerator, denominator)


def _fraction_string_to_decimal(fraction):
    """
    Convert strings such as '1/4' to a Decimal
    """
    parts = fraction.split('/')
    numerator = int(parts[0])
    denominator = int(parts[1])
    return Decimal(numerator / denominator)


def get_fraction_parts(value, allow_mixed_numbers=True, limit_denominator=None, coerce_thirds=True):
    """
    Takes an `int`, `float`, or :class:`decimal.Decimal` and returns
    a tuple of (whole_number, numerator, denominator).  If allow_mixed_numbers
    is not True, then whole_number will be None.

    :param value: The value to convert to parts of a fraction.
    :param bool allow_mixed_numbers: Defaults to True.  If True, then parts for
        mixed numbers will be created, otherwise improper fractions with a
        whole_number of 0 will be created.  In the case where value is a
        whole number such as 4, if allow_mixed_numbers is True, then
        a tuple of (4, 0, 1) would be returned, otherwise
        (0, 4, 1) would be returned.
    :param int limit_denominator: Defaults to None.  If not None then
        the fraction's denominator will be a maximum of the given number.
    :param bool coerce_thirds:  Defaults to True.  If True
        then .3 repeating is forced to 1/3 rather than 3/10, 33/100, etc.
        and .66 and .67 are forced to 2/3.
    """

    f = fractions.Fraction(value)

    whole_number = 0
    if allow_mixed_numbers and f.numerator >= f.denominator:
        # convert to complex number
        # whole_number = f.numerator // f.denominator
        whole_number, numerator = divmod(f.numerator, f.denominator)
        # f = fractions.Fraction(f.numerator - (whole_number * f.denominator), f.denominator)
        f = fractions.Fraction(numerator, f.denominator)

    if limit_denominator:
        f = f.limit_denominator(limit_denominator)

    if coerce_thirds and (not limit_denominator or limit_denominator > 3):
        # if denominator is limited to less than 3, this would be in opposition to that.
        # if denominator is limited to 3 then this has naturally already been done.
        f = coerce_to_thirds(f)
    return (whole_number, f.numerator, f.denominator)


def get_fraction_unicode_entity(value):
    """
    Returns the html unicode entity for the fraction if one exists or None

    :param value:  The value to get the entity for.
    """
    if not isinstance(value, fractions.Fraction):
        value = fractions.Fraction(value)

    entity = u'&frac%d%d;' % (value.numerator, value.denominator)

    if entity not in HTML_ENTITIES:
        return None
    return entity
