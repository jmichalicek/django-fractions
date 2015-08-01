from __future__ import unicode_literals, absolute_import, division

__version__ = '0.1.0'

from decimal import Decimal
import re

__all__ = [
    'quantity_to_decimal',
]


def is_number(s):
    """
    Determine if the input value is numeric - an int, float, decimal.Decimal,
    or a string such as '1', '1.23', etc.
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
    """
    return bool(re.match(r'^\d+/\d+$', s))


def quantity_to_decimal(quantity_string):
    """
    Take a quantity string and return a decimal.
    Handles one hundred, two hundred, three hundred twenty five,
    1, 1 1/4, 1 and 1/4, 1.25, .25
    """

    if is_number(quantity_string):
        return Decimal(quantity_string)

    if is_fraction(quantity_string):
        return _fraction_string_to_decimal(quantity_string)

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

    return Decimal(sum(number_stack))


def _fraction_string_to_decimal(fraction):
    """
    Convert strings such as '1/4' to a Decimal
    """
    parts = fraction.split('/')
    numerator = int(parts[0])
    denominator = int(parts[1])
    return Decimal(numerator / denominator)
