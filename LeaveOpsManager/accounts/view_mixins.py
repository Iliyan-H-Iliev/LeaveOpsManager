from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin
from django.contrib import messages
from django.shortcuts import redirect

from LeaveOpsManager.accounts.models import HR, Manager, Employee


class OwnerRequiredMixin(AccessMixin):
    def _handle_no_permission(self):
        obj = self.get_object()

        if not self.request.user.is_authenticated or obj != self.request.user:
            return self.handle_no_permission()
        return None

    def get(self, *args, **kwargs):
        response = self._handle_no_permission()
        if response:
            return response
        return super().get(*args, **kwargs)


class CompanyContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.object

        context['company'] = company if company else None
        context['hrs'] = HR.objects.filter(company=company) if company else None
        context['managers'] = Manager.objects.filter(company=company) if company else None
        context['employees'] = Employee.objects.filter(company=company) if company else None

        return context


class UserGroupRequiredMixin(UserPassesTestMixin):
    allowed_groups = []

    def test_func(self):
        return (
                self.request.user.is_authenticated and
                self.request.user.groups.filter(name__in=self.allowed_groups).exists()
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "You are not authorized to access this page.")
            return redirect('login')
        else:
            messages.error(self.request, "Only HR and Company users can register employees.")
            return redirect('index')