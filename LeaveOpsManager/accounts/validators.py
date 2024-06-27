from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta


def validate_date_of_hire(value):
    if value < date(1980, 1, 1) or value > timezone.now().date():
        raise ValidationError("The date of hire must be between 1st January 1980, and today.")


def validate_date_of_birth(value):
    sixteen_years_ago = timezone.now().date() - relativedelta(years=16)
    if value < date(1940, 1, 1) or value > sixteen_years_ago:
        raise ValidationError(
            f"The date of birth must be between 01/01/1940 and {sixteen_years_ago.strftime('%m/%d/%Y')}.")


def phone_number_validator(value):
    if not value.isdigit():
        raise ValidationError("Phone number must contain only digits.")
