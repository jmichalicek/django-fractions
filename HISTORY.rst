.. :changelog:

History
-------

Current
+++++++++


2.0.0 (2020-09-13)
+++++++++
* Dropped support for Django 2.0 and lower and bump major version
* Dropped support for Python 3.4 and lower
* Updated DecimalFractionField to work on Django 2+ where from_db_field() does not take a context argument
  and where the field is expected to have a `context` attribute like DecimalField.
* Cleared out a bunch of Python 2 compatibility code such as how calls to super() are made, usage of six, and
  from __future__ imports.

1.1.0 (2017-06-04)
++++++++++++++++++
* add python 3.6 and django 1.11 to tox.ini - still a bit broken
* convert to matrix for environments in .travis.yml
  because tox only wants to test py3.6 when installed under 3.6
  but will not test 3.5 when running with python 3.6 as the base.
* Remove invalid ROOT_URLCONF from test django config
  There is no urls.py for djfractions, don't tell it to use one.  Older
  django versions were ok with this, but 1.11 is pickier about the correctness.
* add current changes to HISTORY.rst
* Adjust SILENCED_SYSTEM_CHECKS setting during tests
  Django 1.11 is stricter about system checks and will not even run
  the tests where there are some errors we specifically test for due
  to older django versions letting you make these mistakes.
* Added optional max_digits and decimal_places parameters to
  forms.DecimalFractionField so that returned Decimal objects have the
  desired max_digits and decimal_places when not directly tied to a
  models.DecimalField() on a ModelForm

1.0.0 (2016-12-31)
++++++++++++++++++
* Stop subclassing Django's DecimalField and duplicate small amounts of code
  as necessary for db backend compatibility.  Too many things need to be
  handled differently.  Main cause of major version bump.
* Update forms.FractionField to skip over max_digits and decimal_places kwargs which
  will get passed in by models.fields.DecimalFractionField
* Add models.fields.DecimalFractionField.formfield() so that a
  forms.FractionField will be used by default
* Fix quantity_to_decimal and quantity_to_fraction to strip leading and trailing
  spaces before pattern matching and converting to a decimal or fraction
* Allow for leading negative sign with forms.FractionField input values
* Fix is_fraction() to allow leading negative sign
* Add `max_digits` and `decimal_places` params to DecimalFractionField in test model
* Additional test cases for models.fields.DecimalFractionField


0.4.0 (2016-08-29)
++++++++++++++++++

* Added djfractions.models.DecimalFractionField which stores fractions.Fraction values as decimals in the dataase.
* Better usage of tox to test against different Python and Django versions
* Added testing against Django 1.10

0.3.2 (2015-08-28)
++++++++++++++++++

* Fixed boolean logic for when to coerce values to thirds in
  in forms.DecimalFractionField and get_fraction_parts()

0.3.1 (2015-08-12)
++++++++++++++++++

* HISTORY.rst typo fixes
* pypi release version fix

0.3.0 (2015-08-12)
++++++++++++++++++

* Added forms.FractionField which returns fractions.Fraction instances
* Refactoring of common code with new forms.FractionField
* Smarter checking for numeric types throughout the code
* forms.DecimalFractionField.to_python() handles fractions.Fraction values now
* Fixed bug handling negative numbers in quantity_to_decimal()
* Added min_value and max_value to forms.DecimalFractionField
* Made coerce_thirds, limit_denominator, and use_mixed_numbers params to DecimalFractionField
  proper named parameters and not just kwargs.

0.2.1 (2015-08-06)
++++++++++++++++++

* Fixed typo in usage docs

0.2.0 (2015-08-06)
++++++++++++++++++

* display_fraction template tag output is templated so that its formatting can be changed by users
* Added new display_improper_fraction template tag to simplify the common case of wanting to only use
  improper fractions with no whole numbers
* Added unicode_entity to template context for display_fraction and display_improper_fraction so that
  the html entity for common fractions may be used rather than <sup> and <sub> tags
* Refactored lots of code out into smaller, reusable functions
* Added a bunch of test cases

0.1.0 (2015-08-01)
++++++++++++++++++

* First release on PyPI.
