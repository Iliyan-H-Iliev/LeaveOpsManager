from django.http import Http404
from .models import LeaveOpsManagerUser, Company, HR, Manager, Employee


def get_user_by_slug(slug):
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
