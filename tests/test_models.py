from __future__ import print_function
from django.db import models
from django.test import TestCase

import decimal
import fractions

from djfractions.models import DecimalFractionField
from .models import TestModel

class DecimalFractionFieldTest(TestCase):

    def test_field(self):
        f = fractions.Fraction(1, 2)
        test_model = TestModel(data=f)
        test_model.save()
        self.assertEqual(f, test_model.data)

        looked_up_model = TestModel.objects.get(id=test_model.id)
        self.assertEqual(f, looked_up_model.data)
        self.assertIsInstance(looked_up_model.data, fractions.Fraction)

    def test_coerce_thirds(self):
        pass

    def test_thirds_without_coerce(self):
        pass

    def test_set_float(self):
        pass

    def test_set_decimal(self):
        pass
