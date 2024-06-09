from django.db import models


class UserTypeMixin(models.Model):
    class Meta:
        abstract = True

    def get_user_class_name(self):
        return self.__class__.__name__

    @property
    def user_type(self):
        return self.get_user_class_name()


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
