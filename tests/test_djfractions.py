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
    pass
