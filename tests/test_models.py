from django.core import checks
from django.db import models
from django.test import TestCase

import decimal
import fractions

from djfractions.models import DecimalFractionField
import djfractions.forms

from .models import TestModel, BadTestModel


class DecimalFractionFieldTest(TestCase):
    def test_field(self):
        """
        Several tests to ensure that when you save and then retrieve
        again from the db, the values are what is expected.
        """
        one_half = fractions.Fraction(1, 2)
        one_third = fractions.Fraction(1, 3)
        two_thirds = fractions.Fraction(2, 3)
        seven_twelths = fractions.Fraction(7, 12)

        test_model = TestModel(
            defaults=one_half, coerce_thirds_true=one_third, denominator_limited_to_ten=seven_twelths
        )
        test_model.save()
        test_model.refresh_from_db()

        self.assertEqual(one_half, test_model.defaults)
        self.assertIsInstance(test_model.defaults, fractions.Fraction)
        self.assertIsNone(test_model.decimal_places_limited)
        self.assertEqual(one_third, test_model.coerce_thirds_true)
        self.assertEqual(fractions.Fraction(4, 7), test_model.denominator_limited_to_ten)

        # test one third with coerce thirds off and two thirds with coerce thirds on
        test_model.decimal_places_limited = one_third
        test_model.coerce_thirds_true = two_thirds
        test_model.save()
        test_model.refresh_from_db()
        self.assertEqual(fractions.Fraction(3333333333, 10000000000), test_model.decimal_places_limited)
        self.assertEqual(two_thirds, test_model.coerce_thirds_true)

    def test_formfield_method_returns_correct_type(self):
        """
        Test that FractionDecimalField returns a forms.FractionField
        """
        dff = DecimalFractionField(name='frac', max_digits=10, decimal_places=5)
        self.assertIsInstance(dff.formfield(), djfractions.forms.FractionField)

    def test_max_digits_arg_is_required(self):
        """
        Test that the max_digits arg is required and raises and exception if not there
        """

        dff = BadTestModel._meta.get_field('missing_max_digits')
        errors = dff.check()
        self.assertEqual(
            [checks.Error("DecimalFractionFields must define a 'max_digits' attribute.", obj=dff, id='fields.E132')],
            errors,
        )

    def test_decimal_places_arg_is_required(self):
        """
        Test that the decimal_places arg is required and raises an exception if not there
        """
        dff = BadTestModel._meta.get_field('missing_decimal_places')
        errors = dff.check()
        self.assertEqual(
            [
                checks.Error(
                    "DecimalFractionFields must define a 'decimal_places' attribute.", obj=dff, id='fields.E130'
                )
            ],
            errors,
        )
