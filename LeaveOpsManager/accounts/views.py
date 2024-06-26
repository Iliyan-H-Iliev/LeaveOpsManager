from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect

from django.urls import reverse_lazy, reverse
from django.views import generic as views, View
from django.contrib.auth import views as auth_views, login, logout, authenticate, get_user_model

from LeaveOpsManager.accounts.forms import SignupEmployeeForm, SignupCompanyForm, PartialPartialEditManagerForm, \
    PartialEditLeaveOpsManagerUserEditForm, PartialPartialEditHRForm, PartialEditEmployeeForm, EditCompanyForm, \
    FullEditManagerForm, FullEditHRForm, FullEditEmployeeForm, FullEditLeaveOpsManagerUserEditForm
from LeaveOpsManager.accounts.mixins import UserTypeRelatedInstanceMixin
from LeaveOpsManager.accounts.models import Company, HR, Manager, Employee

import logging

from LeaveOpsManager.accounts.utils import get_user_by_slug
from LeaveOpsManager.accounts.view_mixins import UserGroupRequiredMixin, CompanyContextMixin, OwnerRequiredMixin

logger = logging.getLogger(__name__)

UserModel = get_user_model()


class IndexView(views.TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            # messages.info(request, "Please log in to access full features of this page.")
            return render(request, self.template_name)

        # Dictionary to map user types to their respective name attributes
        user_type_map = {
            'Company': lambda u: u.company.company_name,
            'Manager': lambda u: u.manager.full_name,
            'HR': lambda u: u.hr.full_name,
            'Employee': lambda u: u.employee.full_name,
        }

        # Default to None if user type is not found
        full_name = user_type_map.get(user.user_type, lambda u: None)(user) if user.user_type else None

        return render(request, self.template_name, {
            'full_name': full_name,
        })


class SignupCompanyView(views.CreateView):
    template_name = "accounts/register_company.html"
    form_class = SignupCompanyForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("index")

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return not self.request.user.is_authenticated

    def form_valid(self, form):
        # `form_valid` will call `save`
        result = super().form_valid(form)
        login(self.request, form.instance)
        return result

    def form_invalid(self, form):
        logger.warning(f"Failed login attempt: {form.cleaned_data.get('name')}")
        logger.warning(f"Form errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse('profile', kwargs={'slug': self.request.user.slug})
        else:
            return reverse('signin user')


class SignupEmployeeView(UserGroupRequiredMixin, views.CreateView):
    template_name = 'accounts/register_employee.html'
    form_class = SignupEmployeeForm

    # TODO: replace 'success_url' with the actual URL name
    success_url = reverse_lazy("index")
    allowed_groups = ['HR', 'Company']

    # def get(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         messages.info(request, "You are not authorized to access this page.")
    #         return redirect('login')  # Redirect to the login page
    #
    #     if request.user.user_type not in ["HR", "Company"]:
    #         messages.error(request, "Only HR and Company users can register employees.")
    #         return redirect('index')  # Redirect to the home page or any other page
    #
    #     return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    # remaining code...


class ProfileDetailsView(OwnerRequiredMixin, views.DetailView):
    model = UserModel
    template_name = "accounts/details_profile.html"
    context_object_name = 'user_profile'

    # TODO: CHECK IF THIS IS THE RIGHT WAY TO FETCH RELATED MODELS FOR THE USER PROFILE
    # def get_queryset(self):
    #     return super().get_queryset().prefetch_related(
    #         'company__hr_set',  # Prefetch HR instances related to the company
    #         'company__manager_set',  # Prefetch Manager instances related to the company
    #         'company__employee_set'  # Prefetch Employee instances related to the company
    #     )

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        return get_user_by_slug(slug)

    # TODO check if this is the right way to fetch related models for the user profile
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.object
    #
    #     company = user.get_company
    #
    #     context['company'] = company if company else None
    #     context['hrs'] = HR.objects.filter(company=company) if company else None
    #     context['managers'] = Manager.objects.filter(company=company) if company else None
    #     context['employees'] = Employee.objects.filter(company=company) if company else None
    #
    #     return context


class SignInUserView(auth_views.LoginView):
    template_name = "accounts/signin_user.html"
    # TODO change to True
    redirect_authenticated_user = True
    success_url = reverse_lazy("profile")

    def get_success_url(self):
        return reverse('profile', kwargs={'slug': self.request.user.slug})

    def form_valid(self, form):
        # Authenticate the user
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(self.request, user)

            # Redirect to the user's profile
            return HttpResponseRedirect(reverse('profile', kwargs={'slug': user.slug}))

        # If the user is not authenticated, call the parent class's form_valid method
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(f"Failed login attempt: {form.cleaned_data.get('username')}")
        logger.warning(f"Form errors: {form.errors}")
        return super().form_invalid(form)


class ProfileUpdateView(View, UserTypeRelatedInstanceMixin):

    form_mapping = {
        'Manager': PartialPartialEditManagerForm,
        'HR': PartialPartialEditHRForm,
        'Employee': PartialEditEmployeeForm,
        'Company': EditCompanyForm,
    }

    def get(self, request, *args, **kwargs):
        user = request.user
        user_form = PartialEditLeaveOpsManagerUserEditForm(instance=user)
        additional_form = self.form_mapping.get(user.user_type, None)

        if additional_form:
            related_instance = self._get_related_instance(user)
            additional_form = additional_form(instance=related_instance)

        return render(request, 'accounts/edit_profile.html', {
            'user_form': user_form,
            'additional_form': additional_form,
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = PartialEditLeaveOpsManagerUserEditForm(request.POST, instance=user)
        additional_form = self.form_mapping.get(user.user_type, None)

        if additional_form:
            related_instance = self._get_related_instance(user)
            additional_form = additional_form(request.POST, instance=related_instance)

        if user_form.is_valid() and (additional_form is None or additional_form.is_valid()):
            user_form.save()
            if additional_form:
                additional_form.save()
            return redirect('profile', slug=user.slug)

        return render(request, 'accounts/edit_profile.html', {
            'user_form': user_form,
            'additional_form': additional_form,
        })


class FullProfileUpdateView(View):

    def get_object(self, queryset=None):
        #TODO check where can use it
        user_slug = self.kwargs['slug']  # Assume the URL contains the user ID
        return get_object_or_404(UserModel, slug=user_slug)

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        user = self.request.user
        user_to_edit = get_user_by_slug(slug)
        company_name = user.get_company_name

        if user.user_type not in ["HR", "Company"]:
            messages.error(request, "Only HR and Company users can edit profiles.")
            return redirect('index')

        user_form = FullEditLeaveOpsManagerUserEditForm(instance=user_to_edit)
        additional_form = None

        if user_to_edit.user_type == 'Manager':
            additional_form = FullEditManagerForm(instance=user_to_edit.manager)
        elif user_to_edit.user_type == 'HR':
            additional_form = FullEditHRForm(instance=user_to_edit.hr)
        elif user_to_edit.user_type == 'Employee':
            additional_form = FullEditEmployeeForm(instance=user_to_edit.employee)
        elif user_to_edit.user_type == 'Company':
            additional_form = EditCompanyForm(instance=user_to_edit.company)

        return render(request, 'accounts/full_profile_edit.html', {
            'user_form': user_form,
            'additional_form': additional_form,
            "user": user,
            "user_to_edit": user_to_edit,
            "company_name": company_name,
        })

    def post(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        user = self.request.user
        user_to_edit = get_user_by_slug(slug)

        if user_to_edit is None:
            messages.error(request, "User not found.")
            return redirect('index')

        if user.user_type not in ["HR", "Company"]:
            messages.error(request, "Only HR and Company users can edit profiles.")
            return redirect('index')

        user_form = PartialEditLeaveOpsManagerUserEditForm(request.POST or None, instance=user_to_edit)
        additional_form = None

        if user_to_edit.user_type == 'Manager':
            additional_form = PartialPartialEditManagerForm(request.POST, instance=user_to_edit.manager)
        elif user_to_edit.user_type == 'HR':
            additional_form = PartialPartialEditHRForm(request.POST, instance=user_to_edit.hr)
        elif user_to_edit.user_type == 'Employee':
            additional_form = PartialEditEmployeeForm(request.POST, instance=user_to_edit.employee)
        elif user_to_edit.user_type == 'Company':
            additional_form = EditCompanyForm(request.POST, instance=user_to_edit.company)

        if user_form.is_valid() and (additional_form is None or additional_form.is_valid()):
            user_form.save()
            if additional_form:
                additional_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('company members')

        messages.error(request, 'Please correct the error below.')
        return render(request, 'accounts/full_profile_edit.html', {
            'user_form': user_form,
            'additional_form': additional_form,
            'slug': slug,
            'user_to_edit': user_to_edit
        })


def signout_user(request):
    logout(request)
    return redirect('index')


class CompanyMembersView(CompanyContextMixin, views.DetailView):
    model = UserModel
    template_name = "accounts/company_members.html"
    context_object_name = 'company_members'

    # TODO: CHECK IF THIS IS THE RIGHT WAY TO FETCH RELATED MODELS FOR THE USER PROFILE
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'company__hr_set',  # Prefetch HR instances related to the company
            'company__manager_set',  # Prefetch Manager instances related to the company
            'company__employee_set'  # Prefetch Employee instances related to the company
        )

    def get_object(self, queryset=None):
        user = self.request.user

        if user.user_type not in ["HR", "Company"]:
            raise Http404("Only HR and Company users can view company members.")

        company = user.get_company

        if not company:
            raise Http404("User does not belong to any company.")

        return company

    def get(self, request, *args, **kwargs):
        user = request.user
        company = user.get_company
        company_name = company.company_name

        if user.user_type not in ["HR", "Company"]:
            messages.error(request, "Only HR and Company users can view company members.")
            return redirect('index')

        if not company:
            messages.error(request, "User does not belong to any company.")
            return redirect('index')

        return render(request, self.template_name, {
            'company': company,
            'company_name': company_name,
            'hrs': HR.objects.filter(company=company),
            'managers': Manager.objects.filter(company=company),
            'employees': Employee.objects.filter(company=company),
        })

    # # TODO check if this is the right way to fetch related models for the user profile
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     company = self.object
    #
    #     context['company'] = company if company else None
    #     context['hrs'] = HR.objects.filter(company=company) if company else None
    #     context['managers'] = Manager.objects.filter(company=company) if company else None
    #     context['employees'] = Employee.objects.filter(company=company) if company else None
    #
    #     return context
