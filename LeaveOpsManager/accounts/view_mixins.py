from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect


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