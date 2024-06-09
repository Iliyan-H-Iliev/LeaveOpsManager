from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from django.utils.timezone import now

from django.contrib.auth.models import Group

from .models import EmployeeProfileBase, Company, Manager, HR, Employee

UserModel = get_user_model()

USER_ROLES = (
    ("Employee", "Employee"),
    ("Manager", "Manager"),
    ("HR", "HR"),
)


class SignupCompanyForm(UserCreationForm):
    company_name = forms.CharField(
        max_length=Company.MAX_COMPANY_NAME_LENGTH,
        min_length=Company.MIN_COMPANY_NAME_LENGTH,
        required=True,
    )

    class Meta:
        model = UserModel
        fields = ["company_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()

        # TODO move slug generation to model

        slug = slugify(f"{self.cleaned_data['company_name']}-{get_random_string(5)}")
        while Company.objects.filter(slug=slug).exists():
            slug = slugify(f"{self.cleaned_data['company_name']}-{get_random_string(5)}")
        company = Company.objects.create(
            company_name=self.cleaned_data["company_name"],
            user=user,
            slug=slug
        )
        if commit:
            company.save()
        user.user_company.add(company)
        user.save()
        return user


class SignupEmployeeForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=EmployeeProfileBase.MAX_FIRST_NAME_LENGTH,
        min_length=EmployeeProfileBase.MIN_FIRST_NAME_LENGTH,
        required=True
    )
    last_name = forms.CharField(
        max_length=EmployeeProfileBase.MAX_LAST_NAME_LENGTH,
        min_length=EmployeeProfileBase.MIN_LAST_NAME_LENGTH,
        required=True
    )

    email = forms.EmailField(
        required=True
    )

    employee_id = forms.CharField(
        max_length=EmployeeProfileBase.MAX_EMPLOYEE_ID_LENGTH,
        required=True
    )
    role = forms.ChoiceField(
        choices=USER_ROLES,
        required=True
    )
    managed_by = forms.ModelChoiceField(
        queryset=Manager.objects.none(),
        required=False,
    )

    # TODO FIX  RANGE
    date_of_hire = forms.DateField(
        required=True,
        widget=forms.SelectDateWidget(years=range(1980, now().year + 1)),
    )
    days_off_left = forms.IntegerField(
        required=True
    )

    # company = forms.CharField(
    #     queryset=Company.objects.all().filter(company_name=user.company),
    # )

    password1 = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
    )
    # TODO FIX MAX_LENGTH
    manages_team = forms.CharField(
        max_length=50,
        required=False,
    )

    class Meta:
        model = UserModel
        fields = [
            "first_name",
            "last_name",
            "email",
            "employee_id",
            "date_of_hire",
            "role",
            "managed_by",
            "days_off_left",
        ]

    def clean(self):
        cleaned_data = super().clean()

        role = cleaned_data.get("role")

        if role == "Employee":
            if not cleaned_data.get("managed_by"):
                self.add_error("managed_by", "Managed by is required for Employee role")

        if role == "Manager":
            if not cleaned_data.get("manages_team"):
                self.add_error("manages_team", "Manages Team is required for Manager role")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        # company_instance = kwargs.pop("company_instance", None)
        super(SignupEmployeeForm, self).__init__(*args, **kwargs)

        # user_instance = self.request.user
        #
        # company_name = user_instance.company
        #
        # company_instance = user_instance.company.first()

        if not self.request.user.is_authenticated:
            raise forms.ValidationError("You must be authenticated to register employees and managers.")

        user_company = None
        # Check if the user belongs to the 'HR' group
        if self.request.user.groups.filter(name='HR').exists():
            hr_profile = self.request.user.hr.first()
            if hr_profile:
                user_company = hr_profile.company

        # Check if the user belongs to the 'Company' group
        elif self.request.user.groups.filter(name='Company').exists():
            # Get the company associated with the user
            user_company = self.request.user.company.first()

        if not user_company:
            raise forms.ValidationError("Only HR and Company users can register employees and managers.")

        # Filter the manager queryset based on the user's company
        self.fields['managed_by'].queryset = Manager.objects.filter(company=user_company)
        self.fields['company'] = forms.ModelChoiceField(
            queryset=Company.objects.filter(pk=user_company.pk),
            disabled=True,
            initial=user_company.pk,
            required=False,
            widget=forms.HiddenInput(),
        )
        self.fields["managed_by"].queryset = Manager.objects.filter(company=user_company)
        self.fields["manages_team"].queryset = Manager.objects.filter(manages_team=Manager.manages_team)
        # self.fields["company"].widget = forms.HiddenInput()
        self.fields["password1"].widget = forms.HiddenInput()
        self.fields["password2"].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = UserModel.objects.create_user(
            email=self.cleaned_data["email"],
            # todo UserModel.objects.make_random_password(), is_active=False
            password="ilich3",
            is_active=True,
        )
        # TODO Move slug generation to model
        slug = slugify(
            f"{self.cleaned_data['first_name']}-{self.cleaned_data['last_name']}-{self.cleaned_data['employee_id']}")

        common_data = {
            "first_name": self.cleaned_data["first_name"],
            "last_name": self.cleaned_data["last_name"],
            "employee_id": self.cleaned_data["employee_id"],
            "user": user,
            "managed_by": self.cleaned_data["managed_by"],
            "date_of_hire": self.cleaned_data["date_of_hire"],
            "days_off_left": self.cleaned_data["days_off_left"],
            "company": self.cleaned_data["company"],
            "slug": slug,
        }

        if self.cleaned_data["role"] == "HR":
            employee = HR.objects.create(**common_data)
        elif self.cleaned_data["role"] == "Manager":
            employee = Manager.objects.create(**common_data, manages_team=self.cleaned_data["manages_team"])
        else:
            employee = Employee.objects.create(**common_data)

        if commit:
            employee.save()
            #
            # # Send email to user with link to reset password and login
            # reset_password_url = self.request.build_absolute_uri(
            #     reverse('password_reset')  # Assuming you have a named URL for password reset
            # )
            # send_mail(
            #     'Welcome to the Company',
            #     f'Please reset your password using the following link: {reset_password_url}',
            #     'from@example.com',
            #     [user.email],
            #     fail_silently=False,
            # )

        return user
