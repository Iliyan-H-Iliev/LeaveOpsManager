from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect

from django.urls import reverse_lazy, reverse
from django.views import generic as views
from django.contrib.auth import views as auth_views, login, logout, authenticate

from LeaveOpsManager.accounts.forms import SignupEmployeeForm, SignupCompanyForm
from LeaveOpsManager.accounts.models import LeaveOpsManagerUser, Company, HR, Manager, Employee

import logging

logger = logging.getLogger(__name__)


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


class SignupEmployeeView(views.CreateView):
    template_name = 'accounts/register_employee.html'
    form_class = SignupEmployeeForm

    # TODO: replace 'success_url' with the actual URL name
    success_url = reverse_lazy("index")

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


class ProfileDetailsView(views.DetailView):
    model = LeaveOpsManagerUser
    template_name = "accounts/details_profile.html"
    context_object_name = 'user_profile'

    # TODO: CHECK IF THIS IS THE RIGHT WAY TO FETCH RELATED MODELS FOR THE USER PROFILE
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
        for model in [Company, HR, Manager, Employee]:
            try:
                user = LeaveOpsManagerUser.objects.get(**{f"{model.__name__.lower()}__slug": slug})
                break
            except LeaveOpsManagerUser.DoesNotExist:
                continue

        if user is None:
            raise Http404("No user found matching the query")

        return user

    # TODO check if this is the right way to fetch related models for the user profile
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.object

        # Get the related company instance

        # if user_profile.company.first():
        #     company = user_profile.company.first()
        # elif user_profile.hr.first():
        #     company = user_profile.hr.first().company
        # elif user_profile.manager.first():
        #     company = user_profile.manager.first().company
        # elif user_profile.employee.first():
        #     company = user_profile.employee.first().company
        # else:

        # company = None

        company = (
                user_profile.company or
                (user_profile.hr and user_profile.hr.company) or
                (user_profile.manager and user_profile.manager.company) or
                (user_profile.employee and user_profile.employee.company)
        )

        # Only attempt to get related instances if the company exists
        if company:
            context['company'] = company
            context['hrs'] = HR.objects.filter(company=company)
            context['managers'] = Manager.objects.filter(company=company)
            context['employees'] = Employee.objects.filter(company=company)
        else:
            context['company'] = None
            context['hrs'] = None
            context['managers'] = None
            context['employees'] = None

        return context


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