from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from django.utils.timezone import now

from .models import EmployeeProfileBase, Company, Manager, HR, Employee

UserModel = get_user_model()

employee_edit_fields = [
    'first_name',
    'last_name',
    'employee_id',
    'managed_by',
    'date_of_hire',
    'days_off_left',
    "phone_number",
    "address", "date_of_birth",
    "profile_picture",
]
user_edit_fields = ['email']
company_edit_fields = ['company_name']


class SignupCompanyForm(UserCreationForm):
    company_name = forms.CharField(
        max_length=Company.MAX_COMPANY_NAME_LENGTH,
        min_length=Company.MIN_COMPANY_NAME_LENGTH,
        required=True,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}),
    )

    class Meta:
        model = UserModel
        fields = ["company_name", "email", "password1", "password2"]

    def save(self, commit=True):

        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.user_type = "Company"
        if commit:
            user.save()

        company = Company.objects.create(
            company_name=self.cleaned_data["company_name"],
            user=user,
        )

        user.company = company

        if commit:
            company.save()
            user.save()
        return user


class SignupEmployeeForm(UserCreationForm):
    USER_ROLES = (
        ("Employee", "Employee"),
        ("Manager", "Manager"),
        ("HR", "HR"),
    )

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
        super().__init__(*args, **kwargs)

        if not self.request:
            raise forms.ValidationError("You must be authenticated to register employees.")

        user = self.request.user

        if not user or not user.is_authenticated:
            raise forms.ValidationError("You must be authenticated to register employees.")

        if user.user_type not in ["HR", "Company"]:
            raise forms.ValidationError("Only HR and Company users can register employees and managers.")

        company = user.get_company

        if not company:
            raise forms.ValidationError("You must be associated with a company to register employees")

        self.fields['company'] = forms.ModelChoiceField(
            queryset=Company.objects.filter(pk=company.pk),
            disabled=True,
            initial=company.pk,
            required=False,
            widget=forms.HiddenInput(),
        )
        self.fields["managed_by"].queryset = Manager.objects.filter(company=company)
        self.fields["manages_team"].queryset = Manager.objects.filter(manages_team=Manager.manages_team)
        self.fields["password1"].widget = forms.HiddenInput()
        self.fields["password2"].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = UserModel.objects.create_user(
            email=self.cleaned_data["email"],
            # todo UserModel.objects.make_random_password(), is_active=False
            user_type=self.cleaned_data["role"],
            password="ilich3",
            is_active=True,

        )

        common_data = {
            "first_name": self.cleaned_data["first_name"],
            "last_name": self.cleaned_data["last_name"],
            "employee_id": self.cleaned_data["employee_id"],
            "user": user,
            "managed_by": self.cleaned_data["managed_by"],
            "date_of_hire": self.cleaned_data["date_of_hire"],
            "days_off_left": self.cleaned_data["days_off_left"],
            "company": self.cleaned_data["company"],
        }

        if self.cleaned_data["role"] == "HR":
            employee = HR.objects.create(**common_data)
        elif self.cleaned_data["role"] == "Manager":
            employee = Manager.objects.create(**common_data, manages_team=self.cleaned_data["manages_team"])
        else:
            employee = Employee.objects.create(**common_data)

        if commit:
            employee.save()
            # TODO Send Email
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


class PartialEditLeaveOpsManagerUserEditForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['email']


# TODO only company can edit company name and company email
class EditCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["company_name"]


class PartialEditEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name',
            'last_name',
            'employee_id',
            'managed_by',
            'date_of_hire',
            'days_off_left',
            "phone_number",
            "address",
            "date_of_birth",
            "profile_picture"
        ]  # Add other fields you want to edit

    def __init__(self, *args, **kwargs):
        super(PartialEditEmployeeForm, self).__init__(*args, **kwargs)
        self.fields['managed_by'].disabled = True
        self.fields['first_name'].disabled = True
        self.fields['last_name'].disabled = True
        self.fields['employee_id'].disabled = True
        self.fields['date_of_hire'].disabled = True
        self.fields['days_off_left'].disabled = True


class PartialPartialEditManagerForm(PartialEditEmployeeForm):
    class Meta(PartialEditEmployeeForm.Meta):
        model = Manager


class PartialPartialEditHRForm(PartialEditEmployeeForm):
    class Meta(PartialEditEmployeeForm.Meta):
        model = HR


class FullEditLeaveOpsManagerUserEditForm(PartialEditLeaveOpsManagerUserEditForm):
    class Meta:
        model = UserModel
        fields = PartialEditLeaveOpsManagerUserEditForm.Meta.fields + ['is_active']


class FullEditEmployeeForm(PartialEditEmployeeForm):
    def __init__(self, *args, **kwargs):
        super(PartialEditEmployeeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].disabled = False


class FullEditHRForm(FullEditEmployeeForm):
    class Meta(FullEditEmployeeForm.Meta):
        model = HR


class FullEditManagerForm(FullEditEmployeeForm):
    class Meta(FullEditEmployeeForm.Meta):
        model = Manager
        fields = FullEditEmployeeForm.Meta.fields + ["manages_team"]
