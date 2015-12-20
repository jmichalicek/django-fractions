from __future__ import print_function, division, absolute_import, unicode_literals
from django.db import models
from django.test import TestCase

import decimal
import fractions

from djfractions.models import DecimalFractionField
from .models import TestModel

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
            defaults=one_half, coerce_thirds_true=one_third, denominator_limited_to_ten=seven_twelths)
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
        self.assertEqual(fractions.Fraction(3333333333, 10000000000),
                         test_model.decimal_places_limited)
        self.assertEqual(two_thirds, test_model.coerce_thirds_true)
