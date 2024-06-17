from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify

# from django.contrib.auth import models as auth_models, get_user_model
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.utils import timezone

from LeaveOpsManager.accounts.mixins import UserTypeMixin, AddToGroupMixin, AbstractSlugMixin
from LeaveOpsManager.accounts.validators import validate_date_of_hire, phone_number_validator


class EmployeeProfileBase(UserTypeMixin,AbstractSlugMixin, AddToGroupMixin, models.Model):

    class Meta:
        abstract = True

    MAX_FIRST_NAME_LENGTH = 30
    MIN_FIRST_NAME_LENGTH = 2
    MAX_LAST_NAME_LENGTH = 30
    MIN_LAST_NAME_LENGTH = 2
    MAX_EMPLOYEE_ID_LENGTH = 15
    MAX_PHONE_NUMBER_LENGTH = 15

    first_name = models.CharField(
        max_length=MAX_FIRST_NAME_LENGTH,
        validators=[MinLengthValidator(MIN_FIRST_NAME_LENGTH)],
        blank=False,
        null=False,
    )

    last_name = models.CharField(
        max_length=MAX_LAST_NAME_LENGTH,
        validators=[MinLengthValidator(MIN_LAST_NAME_LENGTH)],
        blank=False,
        null=False,
    )

    employee_id = models.CharField(
        max_length=MAX_EMPLOYEE_ID_LENGTH,
        validators=[MinLengthValidator(MIN_FIRST_NAME_LENGTH)],
        unique=True,
        blank=False,
        null=False,
    )

    date_of_hire = models.DateField(
        validators=[validate_date_of_hire],
        blank=False,
        null=False,
    )

    days_off_left = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
    )

    phone_number = models.CharField(
        max_length=MAX_PHONE_NUMBER_LENGTH,
        validators=[phone_number_validator],
        blank=True,
        null=True)

    address = models.TextField(
        blank=True,
        null=True)

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    profile_picture = models.URLField(
        blank=True,
        null=True,
    )

    def get_slug_identifier(self):
        company_name = self.company.company_name if hasattr(self, 'company') else 'NoCompany'
        return slugify(
            f"Company:{company_name}-"
            f"{self.__class__.__name__}-"
            f"{self.full_name}-"
            f"{self.employee_id}"
        )

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f"{self.full_name} - {self.user_type}"

    # TODO: change the method!
    # def save(self, *args, **kwargs):
    #     company = apps.get_model('accounts', 'Company')
    #     # Now you can use the Company model
    #     # ...
    #     super().save(*args, **kwargs)


#     def delete(self, *args, **kwargs):
#         # Find all employees managed by this employee
#         employees = AbstractEmployee.objects.filter(manager=self)
#         # Find another manager in the same company
#         company_manager = (AbstractEmployee.objects.filter(
#             company=self.company,
#             role__in=['Manager', "HR"]).exclude(id=self.id).first())
#         # If no other manager is found, fallback to another employee or set to None
#         if not company_manager:
#             company_manager = self.company
#         # Reassign manager for all subordinates
#         for employee in employees:
#             employee.manager = company_manager
#             employee.save()
#         # Call the superclass delete method
#         super().delete(*args, **kwargs)

