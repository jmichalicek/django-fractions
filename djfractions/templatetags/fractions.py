import fractions
from decimal import InvalidOperation
from typing import Any

from django import template

# The try/accept is not working with mypy so for now just always use this.
from typing_extensions import TypedDict

from djfractions import DEFAULT_MAX_DENOMINATOR, get_fraction_parts, get_fraction_unicode_entity
from djfractions.exceptions import NoHtmlUnicodeEntity

# try:
#     from typing import TypedDict
# except ImportError:
#     # temporary until all python versions < 3.8 are dropped
#     from typing_extensions import TypedDict


register = template.Library()

# Not sure about this name just yet
class FractionDisplayData(TypedDict):
    whole_number: int
    numerator: int
    denominator: int
    unicode_entity: str
    allow_mixed_numbers: bool


@register.inclusion_tag("djfractions/display_fraction.html", name="display_fraction")
def display_fraction(
    value: Any,
    limit_denominator: int = DEFAULT_MAX_DENOMINATOR,
    allow_mixed_numbers: bool = True,
    coerce_thirds: bool = True,
) -> FractionDisplayData:
    """
    Display a numeric value as an html fraction using
    <sup>numerator</sup>&frasl;<sub>denominator</sub>
    if value is not a whole number.

    :param int limit_denominator: Limit the denominator to this value.  Defaults to 1000000,
        which is the same as :meth:`fractions.Fraction.limit_denominator()` default max_denominator
    :param bool allow_mixed_numbers: Convert to mixed numbers such as 1 1/2 or keep improper
    fractions such as 3/2.  Defaults to True.
    :param bool coerce_thirds:  If True then .3 repeating is forced to 1/3
        rather than 3/10, 33/100, etc. and .66 and .67 are forced to 2/3.
        Defaults to True.
    """

    try:
        whole_number, numerator, denominator = get_fraction_parts(
            value, allow_mixed_numbers, limit_denominator, coerce_thirds
        )
    except (ValueError, InvalidOperation) as e:
        # Could just return early here since it is known that there is no unicode entity for 0/0
        # although technically &infin; would be accurate but probably never what anyone wants
        whole_number, numerator, denominator = (value, 0, 0)

    try:
        unicode_entity = get_fraction_unicode_entity(fractions.Fraction(numerator, denominator))
    except NoHtmlUnicodeEntity as e:
        unicode_entity = ""

    return {
        "whole_number": whole_number,
        "numerator": numerator,
        "denominator": denominator,
        "unicode_entity": unicode_entity,
        "allow_mixed_numbers": allow_mixed_numbers,
    }


@register.inclusion_tag("djfractions/display_fraction.html", name="display_improper_fraction")
def display_improper_fraction(
    value: Any, limit_denominator: int = DEFAULT_MAX_DENOMINATOR, coerce_thirds: bool = True
) -> FractionDisplayData:
    """
    Display a numeric value as an html fraction using
    <sup>numerator</sup>&frasl;<sub>denominator</sub>.
    This tag will never convert to single whole numbers or
    to mixed numbers, it will return improper fractions such as 3/2
    or even 4/1

    :param bool limit_denominator: Limit the denominator to this value.  Defaults to 1000000,
        which is the same as :meth:`fractions.Fraction.limit_denominator()` default max_denominator
    :param bool coerce_thirds:  If True then .3 repeating is forced to 1/3
        rather than 3/10, 33/100, etc. and .66 and .67 are forced to 2/3.
        Defaults to True.
    """
    return display_fraction(
        value, limit_denominator=limit_denominator, allow_mixed_numbers=False, coerce_thirds=coerce_thirds
    )
