from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect

from django.urls import reverse_lazy, reverse
from django.views import generic as views
from django.contrib.auth import views as auth_views, login, logout

from LeaveOpsManager.accounts.forms import RegistrationEmployeeForm, RegistrationCompanyForm
from LeaveOpsManager.accounts.models import  LeaveOpsManagerUser, Company, HR, Manager, Employee


#
# def register_employee(request):
#     if request.method == 'POST':
#         form = RegistrationEmployeeForm(request.POST)
#         if form.is_valid():
#             employee = form.save(commit=False)
#             manager_id = form.cleaned_data.get('manager')
#             manager = get_object_or_404(Employee, id=manager_id)
#             employee.company = manager.company
#             employee.save()
#             return HttpResponse("Employee registered successfully", status=201)
#         else:
#             return HttpResponse("Form is not valid", status=400)
#     else:
#         form = EmployeeForm()
#         return render(request, 'register_employee.html', {'form': form})


class RegistrationCompanyView(views.CreateView):
    template_name = "accounts/register_company.html"
    form_class = RegistrationCompanyForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        # `form_valid` will call `save`
        result = super().form_valid(form)

        login(self.request, form.instance)

        return result


class RegistrationEmployeeView(views.CreateView):
    template_name = 'accounts/register_employee.html'
    form_class = RegistrationEmployeeForm
    # TODO: replace 'success_url' with the actual URL name
    success_url = reverse_lazy('register employee')  # replace 'success_url' with the actual URL name

    # def form_valid(self, form):
    #     employee = form.save(commit=False)
    #     manager_id = form.cleaned_data.get('managed_by')
    #     manager = get_object_or_404(EmployeeProfileBase, id=manager_id)
    #     employee.company = manager.company
    #     employee.save()
    #     return HttpResponse("Employee registered successfully", status=201)
    #
    # def form_invalid(self, form):
    #     return HttpResponse("Form is not valid", status=400)
    #
    # def get(self, request, *args, **kwargs):
    #     form = RegistrationEmployeeForm(request.POST or None, request=request)
    #     return render(request, self.template_name, {'form': form})
    #
    # def post(self, request, *args, **kwargs):
    #     form = RegistrationEmployeeForm(request.POST or None, request=request)
    #     if form.is_valid():
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    # remaining code...


import logging

logger = logging.getLogger(__name__)


class ProfileDetailsView(views.DetailView):
    model = LeaveOpsManagerUser
    template_name = "accounts/details_profile.html"
    context_object_name = 'user_profile'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'company__hr_set',  # Prefetch HR instances related to the company
            'company__manager_set',  # Prefetch Manager instances related to the company
            'company__employee_set'  # Prefetch Employee instances related to the company
        )

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        user = None

        # Try to fetch the user from the related models
        for model in ["user_company", "HRs", "Managers", "Employees"]:


            try:
                user = LeaveOpsManagerUser.objects.get(**{f"{model.lower()}__slug": slug})
                break
            except LeaveOpsManagerUser.DoesNotExist:
                continue

        if user is None:
            raise Http404("No user found matching the query")

        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.object
        slug_url_kwarg = "slug"

        # Get the related company, HR, Manager, and Employee instances
        context['company'] = Company.objects.filter(user=user_profile).first()
        context['hrs'] = HR.objects.filter(company__user=user_profile)
        context['managers'] = Manager.objects.filter(company__user=user_profile)
        context['employees'] = Employee.objects.filter(company__user=user_profile)

        return context




class SignInUserView(auth_views.LoginView):
    template_name = "accounts/signin_user.html"
    # TODO change to True
    redirect_authenticated_user = True
    success_url = reverse_lazy("index")

    def get_success_url(self):
        return reverse('profile', kwargs={'slug': self.request.user.slug})

    def form_invalid(self, form):
        logger.warning(f"Failed login attempt: {form.cleaned_data.get('username')}")
        logger.warning(f"Form errors: {form.errors}")
        return super().form_invalid(form)


# class ProfileUpdateView(views.UpdateView):
#     queryset = Profile.objects.all()
#     template_name = "accounts/edit_profile.html"
#     fields = ("first_name", "last_name", "date_of_birth", "profile_picture")
#
#     def get_success_url(self):
#         return reverse("details profile", kwargs={
#             "pk": self.object.pk,
#         })
#
#     def get_form(self, form_class=None):
#         form = super().get_form(form_class=form_class)
#
#         form.fields["date_of_birth"].widget.attrs["type"] = "date"
#         form.fields["date_of_birth"].label = "Birthday"
#         return form


def signout_user(request):
    logout(request)
    return redirect('index')


class IndexView(views.TemplateView):
    template_name = "index.html"
