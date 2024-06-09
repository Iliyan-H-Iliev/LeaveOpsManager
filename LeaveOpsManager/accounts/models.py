from django.contrib.auth.models import Group, Permission
from django.core.validators import MinLengthValidator
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import models as auth_models

from django.utils import timezone

from .managers import LeaveOpsManagerUserManager

from .base_models import EmployeeProfileBase
from LeaveOpsManager.accounts.mixins import UserTypeMixin


class LeaveOpsManagerUser(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
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

    def get_slug(self):
        if self.user_company.first():
            return self.user_company.first().slug
        if self.hrs.first():
            return self.hrs.first().slug
        if self.managers.first():
            return self.managers.first().slug
        if self.employees.first():
            return self.employees.slug
        return None

    @property
    def slug(self):
        return self.get_slug()

    USERNAME_FIELD = "email"

    objects = LeaveOpsManagerUserManager()


class Meta:
    verbose_name = 'user'
    verbose_name_plural = 'users'


class Company(UserTypeMixin, models.Model):
    MAX_COMPANY_NAME_LENGTH = 50
    MIN_COMPANY_NAME_LENGTH = 3
    MAX_SLUG_LENGTH = 100

    # TODO Add company name to registration form and update the view to save the company name

    company_name = models.CharField(
        max_length=MAX_COMPANY_NAME_LENGTH,
        validators=[MinLengthValidator(MIN_COMPANY_NAME_LENGTH)],
        null=False,
        blank=False,
    )

    days_off_per_year = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
    )

    transferable_days_off = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
    )

    user = models.ForeignKey(
        LeaveOpsManagerUser,
        on_delete=models.CASCADE,
        related_name="user_company",
    )

    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        null=False,
        blank=True,
        editable=False,
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="company_group",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Get or create the 'Company' group
        company_group, created = Group.objects.get_or_create(name='Company')

        # Add the user to the 'Company' group
        self.user.groups.add(company_group)

    def get_all_hrs(self):
        # from .models import HR
        return HR.objects.filter(company=self)

    def get_all_managers(self):
        # from .models import Manager
        return Manager.objects.filter(company=self)

    def __str__(self):
        return self.company_name


class Manager(EmployeeProfileBase):
    MAX_MANAGES_TEAM_LENGTH = 50
    MIN_MANAGES_TEAM_LENGTH = 3

    managed_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='manage_managers',
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="manager_company",
    )

    user = models.ForeignKey(
        LeaveOpsManagerUser,
        on_delete=models.CASCADE,
        related_name="managers",
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
        related_name="manager_group",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Get or create the 'Company' group
        manager_group, created = Group.objects.get_or_create(name='Manager')

        # Add the user to the 'Company' group
        self.user.groups.add(manager_group)


class HR(EmployeeProfileBase):
    managed_by = models.ForeignKey(
        Manager,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='manage_hrs',
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="hr_company",
    )

    user = models.ForeignKey(
        LeaveOpsManagerUser,
        on_delete=models.CASCADE,
        related_name="hrs",
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hr_group",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Get or create the 'Company' group
        hr_group, created = Group.objects.get_or_create(name='HR')

        # Add the user to the 'Company' group
        self.user.groups.add(hr_group)


class Employee(EmployeeProfileBase):
    managed_by = models.ForeignKey(
        Manager,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="manage_employees",
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employee_company",
    )

    user = models.ForeignKey(
        LeaveOpsManagerUser,
        on_delete=models.CASCADE,
        related_name="employees",
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_group",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Get or create the 'Company' group
        employee_group, created = Group.objects.get_or_create(name='Employee')

        # Add the user to the 'Company' group
        self.user.groups.add(employee_group)

    def promote_to_manager(self):
        # Create a new Manager instance with the same attributes as the employee
        manager = Manager.objects.create(
            first_name=self.first_name,
            last_name=self.last_name,
            employee_id=self.employee_id,
            date_of_hire=self.date_of_hire,
            days_off_left=self.days_off_left,
            phone_number=self.phone_number,
            address=self.address,
            date_of_birth=self.date_of_birth,
            profile_picture=self.profile_picture,
            user=self.user,
            company=self.company,
        )

        # Delete the Employee instance
        self.delete()

        return manager
