from __future__ import division, absolute_import, unicode_literals
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.template import Template, Context

from decimal import Decimal
import fractions

from djfractions import quantity_to_decimal, get_fraction_unicode_entity, quantity_to_fraction
from djfractions.forms import DecimalFractionField


class QuantityToDecimalTest(TestCase):
    """
    Test the quantity_to_decimal() function
    """

    def test_single_integer(self):
        self.assertEqual(Decimal(1), quantity_to_decimal('1'))
        self.assertEqual(Decimal(2), quantity_to_decimal('2'))
        self.assertEqual(Decimal(10), quantity_to_decimal('10'))

    def test_simple_decimal(self):
        self.assertEqual(Decimal('.25'), quantity_to_decimal('.25'))
        self.assertEqual(Decimal('1.25'), quantity_to_decimal('1.25'))
        self.assertEqual(Decimal('.3'), quantity_to_decimal('.3'))

    def test_simple_fraction(self):
        self.assertEqual(Decimal('.25'),
                         quantity_to_decimal('1/4').quantize(Decimal('0.00')))
        self.assertEqual(Decimal('.5'),
                         quantity_to_decimal('1/2').quantize(Decimal('0.0')))
        self.assertEqual(Decimal('.3'),
                         quantity_to_decimal('1/3').quantize(Decimal('0.0')))
        self.assertEqual(Decimal('.67'),
                         quantity_to_decimal('2/3').quantize(Decimal('0.00')))

    def test_mixed_number(self):
        self.assertEqual(Decimal('1.25'), quantity_to_decimal('1 1/4'))
        self.assertEqual(Decimal('1.33'),
                         quantity_to_decimal('1 1/3').quantize(Decimal('0.01')))
        self.assertEqual(Decimal('1.25'), quantity_to_decimal('1 and 1/4'))
        self.assertEqual(Decimal('1.25'), quantity_to_decimal('1-1/4'))

    def test_mixed_number(self):
        self.assertEqual(Decimal('-1.25'), quantity_to_decimal('-1 1/4'))
        self.assertEqual(Decimal('-1.33'),
                         quantity_to_decimal('-1 1/3').quantize(Decimal('0.01')))
        self.assertEqual(Decimal('-1.25'), quantity_to_decimal('-1 and 1/4'))
        self.assertEqual(Decimal('-1.25'), quantity_to_decimal('-1-1/4'))



class QuantityToFractionTest(TestCase):
    def test_single_integer(self):
        self.assertEqual(fractions.Fraction(1, 1), quantity_to_fraction('1'))
        self.assertEqual(fractions.Fraction(2, 1), quantity_to_fraction('2'))

    def test_simple_decimal(self):
        self.assertEqual(fractions.Fraction(1, 4), quantity_to_fraction('.25'))
        self.assertEqual(fractions.Fraction(5, 4), quantity_to_fraction('1.25'))

    def test_simple_fraction(self):
        self.assertEqual(fractions.Fraction(1, 4), quantity_to_fraction('1/4'))
        self.assertEqual(fractions.Fraction(1, 3), quantity_to_fraction('1/3'))
        self.assertEqual(fractions.Fraction(3, 2), quantity_to_fraction('3/2'))

    def test_mixed_number(self):
        self.assertEqual(fractions.Fraction(5, 4), quantity_to_fraction('1 1/4'))
        self.assertEqual(fractions.Fraction(5, 4), quantity_to_fraction('1 and 1/4'))
        self.assertEqual(fractions.Fraction(5, 4), quantity_to_fraction('1-1/4'))

    def test_negative_numbers(self):
        self.assertEqual(fractions.Fraction(-5, 4), quantity_to_fraction('-1 1/4'))
        self.assertEqual(fractions.Fraction(-5, 4), quantity_to_fraction('-1-1/4'))
        self.assertEqual(fractions.Fraction(-5, 4), quantity_to_fraction('-1 - 1/4'))
        self.assertEqual(fractions.Fraction(-5, 4), quantity_to_fraction('-1 and 1/4'))

class DisplayFractionTagTest(TestCase):
    """
    Test the quantity_to_decimal() function
    """

    def setUp(self):
        self.template = Template("""
        {% load fractions %}
        {% display_fraction frac %}
        """)

        self.all_params_template = Template("""
        {% load fractions %}
        {% display_fraction frac limit_denominator mixed_numbers coerce_thirds %}
        """)


    def test_whole_number(self):
        c = Context({'frac': 1})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '1')

    def test_simple_fraction(self):
        c = Context({'frac': .5})

        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>1</sup>&frasl;<sub>2</sub>')

        c = Context({'frac': Decimal('.5')})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>1</sup>&frasl;<sub>2</sub>')

    def test_complex_number(self):
        c = Context({'frac': 1.5})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '1 <sup>1</sup>&frasl;<sub>2</sub>')

    def test_limit_denominator(self):
        c = Context(
            {'frac': 1/3.0,
             'limit_denominator': 3,
             'mixed_numbers': True,
             'coerce_thirds': True
         })
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '<sup>1</sup>&frasl;<sub>3</sub>')

    def test_allow_mixed_numbers_with_improper_fraction(self):
        c = Context(
            {'frac': 1.5,
             'limit_denominator': None,
             'mixed_numbers': True,
             'coerce_thirds': True
         })
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '1 <sup>1</sup>&frasl;<sub>2</sub>')

        c = Context(
            {'frac': 1.5,
             'limit_denominator': None,
             'mixed_numbers': False,
             'coerce_thirds': True
         })
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '<sup>3</sup>&frasl;<sub>2</sub>')

    def test_allow_mixed_numbers_with_whole_number_int(self):
        c = Context(
            {'frac': 4,
             'limit_denominator': None,
             'mixed_numbers': True,
             'coerce_thirds': True
        })
        rendered = self.all_params_template.render(c)

        self.assertEqual(rendered.strip(), '4')

        c = Context(
            {'frac': 4,
             'limit_denominator': None,
             'mixed_numbers': False,
             'coerce_thirds': True
         })
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '<sup>4</sup>&frasl;<sub>1</sub>')

    def test_allow_mixed_numbers_with_whole_number_float(self):

        c = Context(
            {'frac': 4.0,
             'limit_denominator': None,
             'mixed_numbers': True,
             'coerce_thirds': True
         })
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '4')

        c = Context(
            {'frac': 4.0,
             'limit_denominator': None,
             'mixed_numbers': False,
             'coerce_thirds': True
         })
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '<sup>4</sup>&frasl;<sub>1</sub>')


    def test_allow_mixed_numbers_with_whole_number_decimal(self):

        c = Context(
            {'frac': Decimal('4.0'),
             'limit_denominator': None,
             'mixed_numbers': True,
             'coerce_thirds': True
         })
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '4')

        c = Context(
            {'frac': Decimal('4.0'),
             'limit_denominator': None,
             'mixed_numbers': False,
             'coerce_thirds': True
         })
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '<sup>4</sup>&frasl;<sub>1</sub>')

    def test_zero_allow_mixed_numbers(self):
        c = Context({'frac': 0})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '0')

    def test_zero_no_mixed_numbers(self):
        c = Context({'frac': 0,
                     'limit_denominator': None,
                     'mixed_numbers': False,
                     'coerce_thirds': True})
        rendered = self.all_params_template.render(c)
        self.assertEqual(rendered.strip(), '<sup>0</sup>&frasl;<sub>1</sub>')


class DisplayImproperFractionTagTest(TestCase):
    """
    Test the display_improper_fraction template tag
    """

    def setUp(self):
        self.template = Template("""
        {% load fractions %}
        {% display_improper_fraction frac %}
        """)

    def test_improper_fraction_float(self):
        c = Context({'frac': 1.5})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>3</sup>&frasl;<sub>2</sub>')

    def test_improper_fraction_decimal(self):
        c = Context({'frac': Decimal('1.5')})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>3</sup>&frasl;<sub>2</sub>')

    def test_whole_number_integer(self):
        c = Context({'frac': 4})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>4</sup>&frasl;<sub>1</sub>')

    def test_whole_number_float(self):
        c = Context({'frac': 4.0})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>4</sup>&frasl;<sub>1</sub>')

    def test_whole_number_decimal(self):
        c = Context({'frac': Decimal('4')})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>4</sup>&frasl;<sub>1</sub>')

    def test_proper_fraction_float(self):
        c = Context({'frac': .5})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>1</sup>&frasl;<sub>2</sub>')

    def test_proper_fraction_decimal(self):
        c = Context({'frac': Decimal('.5')})
        rendered = self.template.render(c)
        self.assertEqual(rendered.strip(), '<sup>1</sup>&frasl;<sub>2</sub>')


class DecimalFractionFieldTest(TestCase):

    def test_prepare_value_int(self):
        """
        Test that a standard int as input is returned
        as a string of that int, so `1` is returned as `'1'`
        """
        field = DecimalFractionField()
        result = field.prepare_value(1)
        self.assertEqual('1', result)

    def test_prepare_value_string(self):
        """
        Test string fractions are returns as is
        """
        field = DecimalFractionField()
        result = field.prepare_value('1/4')
        self.assertEqual('1/4', result)

        result = field.prepare_value('1 1/4')
        self.assertEqual('1 1/4', result)

    def test_prepare_value_decimal(self):
        """
        Test that a :class:`decimal.Decimal` is properly
        converted to a string fraction
        """
        field = DecimalFractionField()
        result = field.prepare_value(Decimal('.5'))
        self.assertEqual('1/2', result)

    def test_prepare_value_float(self):
        """
        Test that a :class:`float` is properly
        converted to a string fraction
        """
        field = DecimalFractionField()
        result = field.prepare_value(float(.5))
        self.assertEqual('1/2', result)

    def test_prepare_value_limit_denominator(self):
        """
        Test `prepare_value()` when the field has been initialized
        with the limit_denominator paramter
        """
        field = DecimalFractionField(limit_denominator=3)
        result = field.prepare_value(Decimal(1/3.0))
        self.assertEqual('1/3', result)

    def test_prepare_value_coerce_thirds(self):
        """
        Test that when coerce_thirds is specified, then .66, .67, and .33, etc.
        are converted properly to 1/3 and 2/3
        """
        field = DecimalFractionField(coerce_thirds=True)
        result = field.prepare_value(Decimal(1/3.0))
        self.assertEqual('1/3', result)

        result = field.prepare_value(Decimal(1/3.0))
        self.assertEqual('1/3', result)

        result = field.prepare_value(Decimal(2/3.0))
        self.assertEqual('2/3', result)

        result = field.prepare_value(Decimal(2/6.0))
        self.assertEqual('1/3', result)

        result = field.prepare_value(Decimal(4/6.0))
        self.assertEqual('2/3', result)

        result = field.prepare_value(Decimal(4/3.0))
        self.assertEqual('1 1/3', result)

        result = field.prepare_value(Decimal(5/3.0))
        self.assertEqual('1 2/3', result)

    def test_to_python_decimal(self):
        """
        Test that whena :class:`decimal.Decimal` is passed to to_python()
        the value is returned as is
        """
        field = DecimalFractionField()
        value = Decimal(.5)
        result = field.to_python(value)
        self.assertEqual(value, result)

    def test_to_python_float(self):
        """
        Test that whena :class:`float` is passed to to_python()
        the value is returned as as :class:`decimal.Decimal`
        """
        field = DecimalFractionField()
        value = .5
        result = field.to_python(value)
        self.assertEqual(Decimal(value), result)

    def test_to_python_int(self):
        """
        Test that whena :class:`int` is passed to to_python()
        the value is returned as as :class:`decimal.Decimal`
        """
        field = DecimalFractionField()
        value = 1
        result = field.to_python(value)
        self.assertEqual(Decimal(value), result)

    def test_to_python_int_string(self):
        field = DecimalFractionField()
        value = '2'
        result = field.to_python(value)
        self.assertEqual(Decimal('2'), result)

    def test_to_python_float_string(self):
        field = DecimalFractionField()
        value = '0.5'
        result = field.to_python(value)
        self.assertEqual(Decimal(value), result)

    def test_to_python_fraction_string(self):
        field = DecimalFractionField()
        value = '1/2'
        result = field.to_python(value)
        self.assertEqual(Decimal('.5'), result)

    def test_to_python_mixed_fraction_string(self):
        field = DecimalFractionField()
        value = '1 1/2'
        result = field.to_python(value)
        self.assertEqual(Decimal(3/2.0).quantize(Decimal('0.000')),
                         result.quantize(Decimal('0.000')))

    def test_to_python_hyphenated_mixed_fraction_string(self):
        field = DecimalFractionField()
        value = '1-1/2'
        result = field.to_python(value)
        self.assertEqual(Decimal(3/2.0).quantize(Decimal('0.000')),
                         result.quantize(Decimal('0.000')))

        value = '1 - 1/2'
        result = field.to_python(value)
        self.assertEqual(Decimal(3/2.0).quantize(Decimal('0.000')),
                         result.quantize(Decimal('0.000')))

    def test_to_python_anded_mixed_fraction_string(self):
        field = DecimalFractionField()
        value = '1 and 1/2'
        result = field.to_python(value)
        self.assertEqual(Decimal(3/2.0).quantize(Decimal('0.000')),
                         result.quantize(Decimal('0.000')))

    def test_to_python_validation_errors(self):
        field = DecimalFractionField()
        with self.assertRaises(ValidationError):
            field.to_python('abcd')

        with self.assertRaises(ValidationError):
            field.to_python('1 1 1/3')

        with self.assertRaises(ValidationError):
            field.to_python('1 1')

    def test_validate_inf_raises_error(self):
        field = DecimalFractionField()
        with self.assertRaises(ValidationError):
            field.validate(Decimal("Inf"))

    def test_validate_negative_inf_raises_error(self):
        field = DecimalFractionField()
        with self.assertRaises(ValidationError):
            field.validate(Decimal("-Inf"))

class GetFractionUnicodeEntityTest(TestCase):

    def test_one_half(self):
        f = fractions.Fraction(1, 2)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac12;', entity)

        entity = get_fraction_unicode_entity(Decimal('.5'))
        self.assertEqual('&frac12;', entity)

    def test_one_third(self):
        f = fractions.Fraction(1, 3)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac13;', entity)

    def test_two_thirds(self):
        f = fractions.Fraction(2, 3)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac23;', entity)

    def test_one_fourth(self):
        f = fractions.Fraction(1, 4)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac14;', entity)

        entity = get_fraction_unicode_entity(Decimal('.25'))
        self.assertEqual('&frac14;', entity)

    def test_three_fourths(self):
        f = fractions.Fraction(3, 4)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac34;', entity)

        entity = get_fraction_unicode_entity(Decimal('.75'))
        self.assertEqual('&frac34;', entity)

    def test_one_fifth(self):
        f = fractions.Fraction(1, 5)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac15;', entity)

        entity = get_fraction_unicode_entity(Decimal('.2'))
        self.assertEqual('&frac15;', entity)

    def test_two_fifths(self):
        f = fractions.Fraction(2, 5)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac25;', entity)

        entity = get_fraction_unicode_entity(Decimal('.4'))
        self.assertEqual('&frac25;', entity)

    def test_three_fifths(self):
        f = fractions.Fraction(3, 5)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac35;', entity)

        entity = get_fraction_unicode_entity(Decimal('.6'))
        self.assertEqual('&frac35;', entity)

    def test_four_fifths(self):
        f = fractions.Fraction(4, 5)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac45;', entity)

        entity = get_fraction_unicode_entity(Decimal('.8'))
        self.assertEqual('&frac45;', entity)

    def test_one_sixth(self):
        f = fractions.Fraction(1, 6)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac16;', entity)

    def test_five_sixths(self):
        f = fractions.Fraction(5, 6)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac56;', entity)

    def test_one_seventh(self):
        f = fractions.Fraction(1, 7)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac17;', entity)

    def test_one_eighth(self):
        f = fractions.Fraction(1, 8)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac18;', entity)

        entity = get_fraction_unicode_entity(Decimal('.125'))
        self.assertEqual('&frac18;', entity)

    def test_three_eighths(self):
        f = fractions.Fraction(3, 8)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac38;', entity)

        entity = get_fraction_unicode_entity(Decimal('.375'))
        self.assertEqual('&frac38;', entity)

    def test_five_eighths(self):
        f = fractions.Fraction(5, 8)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac58;', entity)

        entity = get_fraction_unicode_entity(Decimal('.625'))
        self.assertEqual('&frac58;', entity)

    def test_seven_eighths(self):
        f = fractions.Fraction(7, 8)
        entity = get_fraction_unicode_entity(f)
        self.assertEqual('&frac78;', entity)

        entity = get_fraction_unicode_entity(Decimal('.875'))
        self.assertEqual('&frac78;', entity)
