from django.contrib import admin

from LeaveOpsManager.accounts.models import LeaveOpsManagerUser, Company, Manager, Employee, HR


# Register your models here.
@admin.register(LeaveOpsManagerUser)
class LeaveOpsManagerUserAdmin(admin.ModelAdmin):

    list_display = [
        'email',
        'date_joined',
        'is_staff',
        'is_active',
    ]

    search_fields = [
        'email',
        'date_joined',
    ]

    list_filter = [
        'is_staff',
        'is_active',
    ]

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = [
        'company_name',
        'user',
    ]

    search_fields = [
        'company_name',
        'user',
    ]

    list_filter = [
        'company_name',
        'user',
    ]

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):

    list_display = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]

    search_fields = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]

    list_filter = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]


@admin.register(HR)
class HRAdmin(admin.ModelAdmin):

    list_display = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]

    search_fields = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]

    list_filter = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]

    search_fields = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]

    list_filter = [
        'first_name',
        'last_name',
        'employee_id',
        'date_of_hire',
        'days_off_left',
        'phone_number',
        'address',
        'date_of_birth',
        'profile_picture',
        'company',
    ]