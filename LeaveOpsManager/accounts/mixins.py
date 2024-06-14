from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import Group


class UserTypeMixin(models.Model):
    class Meta:
        abstract = True

    def get_user_class_name(self):
        return self.__class__.__name__

    @property
    def user_type(self):
        return self.get_user_class_name()


class AbstractSlugMixin(models.Model):
    MAX_SLUG_LENGTH = 255

    class Meta:
        abstract = True

    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        null=False,
        blank=True,
        editable=False,
    )

    def save(self, *args, **kwargs):
        # super().save(*args, **kwargs)

        if not self.slug:
            self.slug = slugify(f"{self.get_slug_identifier()}")

        super().save(*args, **kwargs)

    def get_slug_identifier(self):
        raise NotImplementedError("Subclasses must implement this method")


# class OwnerRequiredMixin(AccessMixin):
#     """Verify that the current user has this profile."""
#
#     def _handle_no_permission(self):
#         obj = super().get_object()
#
#         if not self.request.user.is_authenticated or obj.user != self.request.user:
#             return self.handle_no_permission()
#
#     def get(self, *args, **kwargs):
#         return self._handle_no_permission() or super().get(*args, **kwargs)
#


class AddToGroupMixin(models.Model):
    group_name = None  # Override in subclasses
    user_field_name = 'user'  # User instance

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Check if group_name is set
        if not self.group_name:
            raise ValueError("The 'group_name' attribute must be set in subclasses of AddToGroupMixin.")

        # Get the user instance
        user = getattr(self, self.user_field_name, None)
        if user is None:
            raise AttributeError(f"The model instance does not have a '{self.user_field_name}' attribute.")

        # Get or create the group
        group, created = Group.objects.get_or_create(name=self.group_name)

        # Add the user to the group if not already a member
        if user.groups.filter(name=self.group_name).exists():
            # User is already in the group, no need to add again
            return

        user.groups.add(group)
        user.save()


