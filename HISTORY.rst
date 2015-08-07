.. :changelog:

History
-------

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
