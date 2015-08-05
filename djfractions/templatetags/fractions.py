from __future__ import unicode_literals, absolute_import, division

from django import template
from django.utils.safestring import mark_safe

from decimal import Decimal
import fractions

from .. import get_fraction_parts

register = template.Library()


@register.simple_tag(name='display_fraction')
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
        if (whole_number or whole_number == 0) and not numerator \
           and allow_mixed_numbers:
            return u'%s' % whole_number

        if whole_number and allow_mixed_numbers:
            fraction_string = u'%d' % whole_number
        else:
            fraction_string = u''

        fraction_string = '%s <sup>%d</sup>&frasl;<sub>%d</sub>' % (fraction_string, numerator, denominator)

    except (ValueError, InvalidOperation) as e:
        fraction_string = u'%s' % value

    return mark_safe(fraction_string.strip())


@register.simple_tag(name='display_improper_fraction')
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
