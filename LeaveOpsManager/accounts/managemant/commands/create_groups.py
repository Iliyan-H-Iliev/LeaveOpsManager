from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from LeaveOpsManager.accounts.models import Company, HR, Manager, Employee


class Command(BaseCommand):
    help = "Create user groups and assign permissions"

    def handle(self, *args, **options):
        company_group, created = Group.objects.get_or_create(name="Company")
        hr_group, created = Group.objects.get_or_create(name="HR")
        manager_group, created = Group.objects.get_or_create(name="Manager")
        employee_group, created = Group.objects.get_or_create(name="Employee")

        # Assign each group to its respective model
        for company in Company.objects.all():
            company.group = company_group
            company.save()

        for hr in HR.objects.all():
            hr.group = hr_group
            hr.save()

        for manager in Manager.objects.all():
            manager.group = manager_group
            manager.save()

        for employee in Employee.objects.all():
            employee.group = employee_group
            employee.save()

        company_permissions = Permission.objects.filter(
            codename__in=[
                "can_change_company"
                "can_delete_company",
                "can_view_company",
                "can_add_user",
                "can_change_user",
                "can_delete_user",
                "can_view_user",
                "can_add_hr",
                "can_change_hr",
                "can_delete_hr",
                "can_view_hr",
                "can_add_manager",
                "can_change_manager",
                "can_delete_manager",
                "can_view_manager",
                "can_add_employee",
                "can_change_employee",
                "can_delete_employee",
                "can_view_employee",
            ])
        hr_permissions = Permission.objects.filter(
            codename__in=[
                "can_add_user",
                "can_change_user",
                "can_delete_user",
                "can_view_user",
                "can_add_hr",
                "can_change_hr",
                "can_delete_hr",
                "can_view_hr",
                "can_add_manager",
                "can_change_manager",
                "can_delete_manager",
                "can_view_manager",
                "can_add_employee",
                "can_change_employee",
                "can_delete_employee",
                "can_view_employee",
            ])
        manager_permissions = [
            "can_change_employee",
            "can_view_employee",
        ]
        employee_permissions = [
            "can_view_employee",
        ]

        company_group.permissions.set(company_permissions)
        hr_group.permissions.set(hr_permissions)
        manager_group.permissions.set(manager_permissions)
        employee_group.permissions.set(employee_permissions)

        self.stdout.write(self.style.SUCCESS("Successfully created groups and assigned permissions"))