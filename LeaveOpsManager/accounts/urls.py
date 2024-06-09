from django.urls import path, include
from django.contrib.auth import views as auth_views

from LeaveOpsManager.accounts.views import RegistrationEmployeeView, RegistrationCompanyView, SignInUserView, \
    signout_user, IndexView, ProfileDetailsView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("employee/", RegistrationEmployeeView.as_view(), name="register employee"),
    path("company/",  RegistrationCompanyView.as_view(), name="register company"),
    path("profile/<slug:slug>", ProfileDetailsView.as_view(), name="profile"),
    path("login/", SignInUserView.as_view(), name="signin user"),
    path("logout/", signout_user, name="signout user"),
]