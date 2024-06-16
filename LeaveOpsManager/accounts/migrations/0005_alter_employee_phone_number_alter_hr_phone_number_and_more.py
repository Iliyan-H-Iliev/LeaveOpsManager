# Generated by Django 5.0.6 on 2024-06-16 21:59

import LeaveOpsManager.accounts.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_employee_phone_number_alter_hr_phone_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[LeaveOpsManager.accounts.validators.phone_number_validator]),
        ),
        migrations.AlterField(
            model_name='hr',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[LeaveOpsManager.accounts.validators.phone_number_validator]),
        ),
        migrations.AlterField(
            model_name='manager',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[LeaveOpsManager.accounts.validators.phone_number_validator]),
        ),
    ]
