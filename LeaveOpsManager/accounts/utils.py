from django.contrib.auth import get_user_model
from django.http import Http404
from .models import Company, HR, Manager, Employee

UserModel = get_user_model()


def get_user_by_slug(slug):
    user = None

    # Try to fetch the user from the related models
    for model in [Company, HR, Manager, Employee]:
        try:
            user = UserModel.objects.get(**{f"{model.__name__.lower()}__slug": slug})
            break
        except UserModel.DoesNotExist:
            continue

    if user is None:
        raise Http404("No user found matching the query")

    return user


def get_related_instance(user):
    if user.user_type == 'Company':
        return user.company
    elif user.user_type == 'HR':
        return user.hr
    elif user.user_type == 'Manager':
        return user.manager
    elif user.user_type == 'Employee':
        return user.employee
    return None
