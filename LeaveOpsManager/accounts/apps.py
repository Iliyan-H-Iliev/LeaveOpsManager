from django.apps import AppConfig

from LeaveOpsManager import accounts


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'LeaveOpsManager.accounts'
