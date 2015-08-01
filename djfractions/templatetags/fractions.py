from __future__ import unicode_literals, absolute_import, division

from django import template
from django.utils.safestring import mark_safe

from decimal import Decimal
import fractions


register = template.Library()


@register.simple_tag(name='display_fraction')
def display_fraction(value, mixed_numbers=True, coerce_thirds=True):
    """
    Display a numeric value as an html fraction using
    <sup>numerator</sup>&frasl;<sub>denominator</sub>
    if value is not a whole number.

    :param bool reduce_fraction: Reduce fractions to lowest terms.  Defaults to True.
    :param bool mixed_numbers: Convert to mixed numbers such as 1 1/2 or keep improper
        fractions such as 3/2.  Defaults to True.
    :param bool coerce_thirds:  If True then .3 repeating is forced to 1/3
        rather than 3/10, 33/100, etc. and .66 and .67 are forced to 2/3.
        Defaults to True.
    """

    f = fractions.Fraction(value)
    dec = Decimal(value).quantize(Decimal('0.00'))

    # this if/elif, or at least part of it, should possibly live after
    # mixed number handling and maybe fraction reduction as well
    if f.denominator == 1:
        return str(f)
    elif coerce_thirds and (dec == Decimal('.33') or dec == Decimal('.3') or
                            dec == Decimal('.67') or dec == Decimal('.6')):
        f = f.limit_denominator(3)

    fraction_string = ''
    if mixed_numbers and f.numerator > f.denominator:
        # convert to mixed number
        int_part = f.numerator // f.denominator
        f = fractions.Fraction(f.numerator - (int_part * f.denominator), f.denominator)
        fraction_string = u'%d' % int_part

    fraction_string = '%s <sup>%d</sup>&frasl;<sub>%d</sub>' % (fraction_string, f.numerator, f.denominator)
    return mark_safe(fraction_string.strip())
