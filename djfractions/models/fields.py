import decimal
import fractions
import logging
from typing import Any, List, Optional, Tuple, Union

from django.core import checks
from django.core.checks.messages import CheckMessage
from django.db.models import Field
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from djfractions import coerce_to_thirds
from djfractions import forms as fraction_forms

logger = logging.getLogger(__name__)


class DecimalFractionField(Field):
    """
    Field which stores values as a Decimal value, but uses
    :class:`fractions.Fraction` for its value
    """

    empty_strings_allowed = False
    # ignoring type checking here because mypy and gettextlazy and django-stubs are fighting
    # possibly only on python 3.7 or django 3.2
    default_error_messages = {
        "invalid": _("'%(value)s' value must be a fraction number."),  # type: ignore
    }
    description = _("Fraction number stored in the database as a Decimal")

    def __init__(
        self,
        verbose_name: Optional[str] = None,
        name: Optional[str] = None,
        max_digits: Optional[int] = None,
        decimal_places: Optional[int] = None,
        limit_denominator: Optional[int] = None,
        coerce_thirds: bool = True,
        **kwargs
    ):
        self.limit_denominator = limit_denominator
        self.coerce_thirds = coerce_thirds

        # for decimal stuff
        self.max_digits, self.decimal_places = max_digits, decimal_places
        super().__init__(verbose_name=verbose_name, name=name, **kwargs)

    @cached_property
    def context(self) -> decimal.Context:
        # TODO: understand what this is and why it now exists and when and why it got added
        return decimal.Context(prec=self.max_digits)

    def check(self, **kwargs) -> List[CheckMessage]:
        errors = super().check(**kwargs)

        digits_errors = self._check_decimal_places()
        digits_errors.extend(self._check_max_digits())
        if not digits_errors:
            errors.extend(self._check_decimal_places_and_max_digits(**kwargs))
        else:
            errors.extend(digits_errors)
        return errors

    def _check_decimal_places(self) -> List[checks.Error]:
        try:
            # ignoring type to make mypy happy, the exception handling deals with this being incorrect
            decimal_places = int(self.decimal_places)  # type: ignore
            if decimal_places < 0:
                raise ValueError()
        except TypeError:
            return [
                checks.Error(
                    "DecimalFractionFields must define a 'decimal_places' attribute.",
                    obj=self,
                    id="fields.E130",
                )
            ]
        except ValueError:
            return [
                checks.Error(
                    "'decimal_places' must be a non-negative integer.",
                    obj=self,
                    id="fields.E131",
                )
            ]
        else:
            return []

    def _check_max_digits(self) -> List[checks.Error]:
        try:
            # ignoring type to make mypy happy, the exception handling deals with this being incorrect
            max_digits = int(self.max_digits)  # type: ignore
            if max_digits <= 0:
                raise ValueError()
        except TypeError:
            return [
                checks.Error(
                    "DecimalFractionFields must define a 'max_digits' attribute.",
                    obj=self,
                    id="fields.E132",
                )
            ]
        except ValueError:
            return [
                checks.Error(
                    "'max_digits' must be a positive integer.",
                    obj=self,
                    id="fields.E133",
                )
            ]
        else:
            return []

    def _check_decimal_places_and_max_digits(self, **kwargs) -> List[checks.Error]:
        # ignoring type to make mypy happy, the exception handling deals with this being incorrect
        if int(self.decimal_places) > int(self.max_digits):  # type: ignore
            return [
                checks.Error(
                    "'max_digits' must be greater or equal to 'decimal_places'.",
                    obj=self,
                    id="fields.E134",
                )
            ]
        return []

    def from_db_value(self, value: Any, expression: Any, connection: Any, *args, **kwargs) -> fractions.Fraction:
        # uses *args and **kwargs to handle the `context` param which django 1.11 passes in but 2.x+ do not.
        # Not sure if I even really need this anymore.
        return self.to_python(value)

    def get_db_prep_save(self, value: Any, connection):
        # return connection.ops.adapt_decimalfield_value(self.to_python(value), self.max_digits, self.decimal_places)
        # for django 1.9 the following will need used.
        if hasattr(connection.ops, "adapt_decimalfield_value"):
            return connection.ops.adapt_decimalfield_value(
                self.get_prep_value(value),
                self.max_digits,
                self.decimal_places,
            )
        else:
            return connection.ops.value_to_db_decimal(self.get_prep_value(value), self.max_digits, self.decimal_places)

    def to_python(self, value: Union[fractions.Fraction, decimal.Decimal, float, int, str]) -> fractions.Fraction:
        if value is None:
            return value

        # probably need similar error handling to
        # https://github.com/django/django/blob/stable/1.8.x/django/db/models/fields/__init__.py#L1598
        return self.to_fraction(value)

    def get_prep_value(
        self, value: Union[fractions.Fraction, decimal.Decimal, float, int, str, None]
    ) -> Union[decimal.Decimal, None]:
        # not super clear, docs sound like this must be overridden and is the
        # reverse of to_python, but
        # django.db.models.fields.DecimalField just calls self.to_python() here
        # TODO:
        # see https://docs.djangoproject.com/en/1.8/howto/custom-model-fields/#converting-python-objects-to-query-values
        # for usage.
        if value is None:
            return value

        if isinstance(value, fractions.Fraction):
            value = float(value)

        return decimal.Decimal(value)

    def to_fraction(self, value: Union[fractions.Fraction, decimal.Decimal, float, int, str]) -> fractions.Fraction:
        fraction_value = fractions.Fraction(value)

        if self.limit_denominator:
            fraction_value = fraction_value.limit_denominator(self.limit_denominator)

        if self.coerce_thirds and (not self.limit_denominator or self.limit_denominator > 3):
            fraction_value = coerce_to_thirds(fraction_value)

        return fraction_value

    def deconstruct(self) -> Tuple[str, str, list, dict]:
        name, path, args, kwargs = super().deconstruct()
        kwargs["limit_denominator"] = self.limit_denominator
        kwargs["coerce_thirds"] = self.coerce_thirds

        # added this
        # copied from decimal field
        if self.max_digits is not None:
            kwargs["max_digits"] = self.max_digits
        if self.decimal_places is not None:
            kwargs["decimal_places"] = self.decimal_places

        return name, path, args, kwargs

    def formfield(
        self,
        form_class: Optional[Any] = fraction_forms.FractionField,
        choices_form_class: Optional[Any] = None,
        **kwargs: Any
    ) -> Any:
        return super().formfield(form_class=form_class, choices_form_class=choices_form_class, **kwargs)

    def get_internal_type(self) -> str:
        # returning DecimalField, since we use the same backing column type as that
        # and this is safer than overriding db_type() and db_check() since that would
        # require maintaining the mapping for every db adapter.
        return "DecimalField"

    def _format(self, value: Union[decimal.Decimal, str, None]) -> Union[str, None]:
        if isinstance(value, str):
            return value
        else:
            return self.format_number(value)

    def format_number(self, value: Union[decimal.Decimal, None]) -> Union[str, None]:
        """
        Formats a number into a string with the requisite number of digits and
        decimal places.
        """
        # Method moved to django.db.backends.utils.
        #
        # It is preserved because it is used by the oracle backend
        # (django.db.backends.oracle.query), and also for
        # backwards-compatibility with any external code which may have used
        # this method.
        from django.db.backends import utils

        return utils.format_number(value, self.max_digits, self.decimal_places)
