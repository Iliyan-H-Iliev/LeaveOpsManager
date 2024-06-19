from django.urls import path, include
from django.contrib.auth import views as auth_views

from LeaveOpsManager.accounts.views import (
    SignInUserView, signout_user, IndexView,
    ProfileDetailsView, SignupEmployeeView, SignupCompanyView, ProfileUpdateView, CompanyMembersView,
    FullProfileUpdateView
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("employee/", SignupEmployeeView.as_view(), name="register employee"),
    path("company/", SignupCompanyView.as_view(), name="register company"),
    path("profile/<slug:slug>", ProfileDetailsView.as_view(), name="profile"),
    path("login/", SignInUserView.as_view(), name="signin user"),
    path("logout/", signout_user, name="signout user"),
    path("profile/edit/<slug:slug>/", ProfileUpdateView.as_view(), name="edit profile"),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("<str:company_name>/company-members/", CompanyMembersView.as_view(), name="company members"),
    path("<str:company_name>/company-members/<slug:slug>/", FullProfileUpdateView.as_view(), name="full profile update"),
]