from django.test import TestCase
from django import template
from django.contrib.auth.models import AnonymousUser
from django.template import Template, Context
from django.template.base import VariableNode
from django.test import RequestFactory
from django.test.utils import override_settings

import mock
from decimal import Decimal

from djfractions import quantity_to_decimal


class DisplayFractionTagTest(TestCase):
    """
    Test the quantity_to_decimal() function
    """

    def test_whole_number(self):
        template = Template("""
        {% load fractions %}
        {% display_fraction 1 %}
        """)
        c = Context({})

        rendered = template.render(c)
        self.assertEqual(rendered.strip(), '1')

    def test_simple_fraction(self):
        template = Template("""
        {% load fractions %}
        {% display_fraction .5 %}
        """)
        c = Context({})

        rendered = template.render(c)
        self.assertEqual(rendered.strip(), '<sup>1</sup>&frasl;<sub>2</sub>')
