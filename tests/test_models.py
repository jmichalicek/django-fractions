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
        print('type is %s' % type(test_model.data))
        test_model.save()
#        self.assertEqual(f, test_model.data)

#        updated = TestModel.objects.get(id=test_model.id)
#        self.assertEqual(f, updated.data)
