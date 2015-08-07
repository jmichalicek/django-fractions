from __future__ import unicode_literals, absolute_import, division

from django import template

from decimal import Decimal, InvalidOperation
import fractions

from .. import get_fraction_parts, get_fraction_unicode_entity


register = template.Library()


@register.inclusion_tag('djfractions/display_fraction.html', name='display_fraction')
def display_fraction(value, limit_denominator=None, allow_mixed_numbers=True,
                     coerce_thirds=True):
    """
    Display a numeric value as an html fraction using
    <sup>numerator</sup>&frasl;<sub>denominator</sub>
    if value is not a whole number.

    :param bool limit_denominator: Limit the denominator to this value.  Defaults to None,
        which in effect results in the :meth:`fractions.Fraction.limit_denominator()`
        default of `1000000`
    :param bool mixed_numbers: Convert to mixed numbers such as 1 1/2 or keep improper
    fractions such as 3/2.  Defaults to True.
    :param bool coerce_thirds:  If True then .3 repeating is forced to 1/3
        rather than 3/10, 33/100, etc. and .66 and .67 are forced to 2/3.
        Defaults to True.
    """

    try:
        whole_number, numerator, denominator = get_fraction_parts(value,
                                                                  allow_mixed_numbers,
                                                                  limit_denominator,
                                                                  coerce_thirds)
        unicode_entity = get_fraction_unicode_entity(fractions.Fraction(numerator, denominator))
    except (ValueError, InvalidOperation) as e:
        whole_number, numerator, denominator, unicode_entity = (value, 0, 0, None)

    return {
        'whole_number': whole_number,
        'numerator': numerator,
        'denominator': denominator,
        'unicode_entity': unicode_entity,
        'allow_mixed_numbers': allow_mixed_numbers,
    }


@register.inclusion_tag('djfractions/display_fraction.html', name='display_improper_fraction')
def display_improper_fraction(value, limit_denominator=None, coerce_thirds=True):
    """
    Display a numeric value as an html fraction using
    <sup>numerator</sup>&frasl;<sub>denominator</sub>.
    This tag will never convert to single whole numbers or
    to mixed numbers, it will return improper fractions such as 3/2
    or even 4/1

    :param bool limit_denominator: Limit the denominator to this value.  Defaults to None,
        which in effect results in the :meth:`fractions.Fraction.limit_denominator()`
        default of `1000000`
    :param bool coerce_thirds:  If True then .3 repeating is forced to 1/3
        rather than 3/10, 33/100, etc. and .66 and .67 are forced to 2/3.
        Defaults to True.
    """
    return display_fraction(value, limit_denominator=limit_denominator,
                            allow_mixed_numbers=False, coerce_thirds=coerce_thirds)
