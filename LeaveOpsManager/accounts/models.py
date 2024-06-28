from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Model
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import models as auth_models

from django.utils import timezone

from .managers import LeaveOpsManagerUserManager

from .base_models import EmployeeProfileBase, CreatedModifiedMixin
from LeaveOpsManager.accounts.mixins import UserTypeMixin, AddToGroupMixin, AbstractSlugMixin

user_slug_mapping = {
    'company': lambda self: self.company.slug if hasattr(self, 'company') else None,
    'hr': lambda self: self.hr.slug if hasattr(self, 'hr') else None,
    'manager': lambda self: self.manager.slug if hasattr(self, 'manager') else None,
    'employee': lambda self: self.employee.slug if hasattr(self, 'employee') else None
}

user_company_mapping = {
    "company": lambda self: self.company if hasattr(self, 'company') else None,
    "hr": lambda self: self.hr.company if hasattr(self, 'hr') else None,
    "manager": lambda self: self.manager.company if hasattr(self, 'manager') else None,
    "employee": lambda self: self.employee.company if hasattr(self, 'employee') else None
}


class LeaveOpsManagerUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    MAX_USER_TYPE_LENGTH = 20
    MAX_SLUG_LENGTH = 100

    CHOICES_USER_TYPE = (
        ('Company', 'Company'),
        ('HR', 'HR'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="leaveoppsmanagerusers",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="leaveoppsmanagerusers",
        related_query_name="user",
    )

    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    is_staff = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    user_type = models.CharField(
        max_length=MAX_USER_TYPE_LENGTH,
        choices=CHOICES_USER_TYPE,
        default='Employee',
        blank=False,
        null=False,
    )

    # TODO add user_type to the registration form and update the view to save the user_type

    def get_user_slug(self):
        user_type = self.user_type.lower()
        get_slug_function = user_slug_mapping.get(user_type)
        if get_slug_function:
            return get_slug_function(self)
        return None

    @property
    def slug(self):
        return self.get_user_slug()

    def get_user_company(self):
        user_type = self.user_type.lower()
        get_company_function = user_company_mapping.get(user_type)
        if get_company_function:
            return get_company_function(self)
        return None

    @property
    def get_company(self):
        return self.get_user_company() if self.get_user_company() else None

    @property
    def get_company_name(self):
        company = self.get_user_company()
        return company.company_name if company else None

    @property
    def get_user_related_type(self):
        user_type = self.user_type.lower()
        return getattr(self, user_type, None)

    USERNAME_FIELD = "email"

    objects = LeaveOpsManagerUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Company(UserTypeMixin, AbstractSlugMixin, AddToGroupMixin,  CreatedModifiedMixin):
    MAX_COMPANY_NAME_LENGTH = 50
    MIN_COMPANY_NAME_LENGTH = 3
    DEFAULT_DAYS_OFF_PER_YEAR = 0
    DEFAULT_TRANSFERABLE_DAYS_OFF = 0
    RANDOM_STRING_LENGTH = 10

    group_name = 'Company'

    id = models.AutoField(primary_key=True)

    # TODO Add company name to registration form and update the view to save the company name

    company_name = models.CharField(
        max_length=MAX_COMPANY_NAME_LENGTH,
        validators=[MinLengthValidator(MIN_COMPANY_NAME_LENGTH)],
        null=False,
        blank=False,
    )

    days_off_per_year = models.PositiveIntegerField(
        default=DEFAULT_DAYS_OFF_PER_YEAR,
        null=False,
        blank=False,
    )

    transferable_days_off = models.PositiveIntegerField(
        default=DEFAULT_TRANSFERABLE_DAYS_OFF,
        null=False,
        blank=False,
    )

    user = models.OneToOneField(
        LeaveOpsManagerUser,
        on_delete=models.CASCADE,
        related_name="company",
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="company",
    )

    def get_slug_identifier(self):
        return slugify(f"{self.__class__.__name__}-{self.company_name}-{get_random_string(self.RANDOM_STRING_LENGTH)}")

    def get_all_hrs(self):
        return HR.objects.filter(company=self)

    def get_all_managers(self):
        return Manager.objects.filter(company=self)

    def get_all_employees(self):
        return Employee.objects.filter(company=self)

    def get_all_company_members(self):
        return self.get_all_hrs() | self.get_all_managers() | self.get_all_employees()

    def __str__(self):
        return self.company_name


class Manager(EmployeeProfileBase):
    MAX_MANAGES_TEAM_LENGTH = 50
    MIN_MANAGES_TEAM_LENGTH = 3

    group_name = 'Manager'

    managed_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='manages_managers',
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="managers",
    )

    user = models.OneToOneField(
        LeaveOpsManagerUser,
        on_delete=models.CASCADE,
        related_name="manager",
    )

    # TODO NULL TRUE BLANK TRUE
    manages_team = models.CharField(
        max_length=MAX_MANAGES_TEAM_LENGTH,
        validators=[MinLengthValidator(MIN_MANAGES_TEAM_LENGTH)],
        null=False,
        blank=False,
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="manager",
    )


class HR(EmployeeProfileBase):
    group_name = 'HR'

    managed_by = models.ForeignKey(
        Manager,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='manages_hrs',
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="hrs",
    )

    user = models.OneToOneField(
        LeaveOpsManagerUser,
        on_delete=models.CASCADE,
        related_name="hr",
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hr",
    )


class Employee(EmployeeProfileBase):
    group_name = 'Employee'



    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employees",
    )

    user = models.OneToOneField(
        LeaveOpsManagerUser,
        on_delete=models.CASCADE,
        related_name="employee",
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee",
    )

    shift_pattern = models.ForeignKey(
        'team_management.ShiftPattern',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    team = models.ForeignKey(
        'team_management.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    managed_by = models.ForeignKey(
        Manager,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="manages_employees",
    )


    # def promote_to_manager(self):
    #     # Create a new Manager instance with the same attributes as the employee
    #     manager = Manager.objects.create(
    #         first_name=self.first_name,
    #         last_name=self.last_name,
    #         employee_id=self.employee_id,
    #         date_of_hire=self.date_of_hire,
    #         days_off_left=self.days_off_left,
    #         phone_number=self.phone_number,
    #         address=self.address,
    #         date_of_birth=self.date_of_birth,
    #         profile_picture=self.profile_picture,
    #         user=self.user,
    #         company=self.company,
    #     )
    #
    #     # Delete the Employee instance
    #     self.delete()
    #
    #     return manager


