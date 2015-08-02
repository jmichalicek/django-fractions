from __future__ import division, absolute_import, unicode_literals
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.template import Template, Context

from decimal import Decimal

from djfractions import quantity_to_decimal
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

    def test_complex_number(self):
        self.assertEqual(Decimal('1.25'), quantity_to_decimal('1 1/4'))
        self.assertEqual(Decimal('1.33'),
                         quantity_to_decimal('1 1/3').quantize(Decimal('0.01')))
        self.assertEqual(Decimal('1.25'), quantity_to_decimal('1 and 1/4'))
        self.assertEqual(Decimal('1.25'), quantity_to_decimal('1-1/4'))


class DisplayFractionTagTest(TestCase):
    """
    Test the quantity_to_decimal() function
    """

    def setUp(self):
        self.template = Template("""
        {% load fractions %}
        {% display_fraction frac %}
        """)

        self.template_reduce_false = Template("""
        {% load fractions %}
        {% display_fraction frac False %}
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


class DecimealFractionFieldTest(TestCase):

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
