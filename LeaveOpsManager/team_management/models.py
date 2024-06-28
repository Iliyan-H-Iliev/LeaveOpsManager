from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator, MaxValueValidator
from django.utils import timezone
from LeaveOpsManager.accounts.models import Manager, Company, Employee
from datetime import date, timedelta
from django.core.exceptions import ObjectDoesNotExist



class ShiftPattern(models.Model):
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 50
    MIN_ROTATION_WEEKS = 1
    MAX_ROTATION_WEEKS = 52

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='shift_patterns',
        blank=False,
        null=False,
    )

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        validators=[MinLengthValidator(MIN_NAME_LENGTH)],
        blank=False,
        null=False,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    start_date = models.DateField(
        default=timezone.now,
        blank=False,
        null=False,
    )

    rotation_weeks = models.IntegerField(
        default=MIN_ROTATION_WEEKS,
        validators=[
            MinValueValidator(MIN_ROTATION_WEEKS),
            MaxValueValidator(MAX_ROTATION_WEEKS),
        ],
        blank=False,
        null=False,
    )

    def generate_shift_working_dates(self):
        # end_date = date(date.today().year + 1, 12, 31)
        days = []
        current_date = self.start_date
        end_date = current_date + timedelta(days=30)
        for block in self.blocks.all():
            block.working_dates.clear()
            days += block.working_days

        while current_date <= end_date:
            for block in self.blocks.all():
                for day in block.working_days:
                    if current_date > end_date:
                        break
                    if day == 1:  # Only create assignments for working days
                        date_obj, created = Date.objects.get_or_create(date=current_date)
                        block.working_dates.add(date_obj)
                    current_date += timedelta(days=1)



    # rotation_weeks = models.PositiveIntegerField(
    #     default=MIN_ROTATION_WEEKS,
    #     validators=[
    #         MinValueValidator(MIN_ROTATION_WEEKS),
    #         MaxValueValidator(MAX_ROTATION_WEEKS)
    #     ],
    #     blank=False,
    #     null=False,
    # )

    class Meta:
        unique_together = ('company', 'name')

    def __str__(self):
        return f"{self.name}"


class ShiftBlock(models.Model):

    pattern = models.ForeignKey(
        ShiftPattern,
        on_delete=models.CASCADE,
        related_name='blocks'
    )

    working_days = ArrayField(
        models.IntegerField(),
        size=20,
        blank=False,
        null=False,
    )
    start_time = models.TimeField(
        blank=False,
        null=False,
    )

    end_time = models.TimeField(
        blank=False,
        null=False,
    )

    duration = models.DurationField(
        blank=True,
        null=True,
    )

    order = models.PositiveIntegerField(
        blank=False,
        null=False,
    )

    working_dates = models.ManyToManyField(
        'Date',
        related_name='shift_blocks',
        blank=True,
    )

    class Meta:
        ordering = ['order']

    # def __str__(self):
    #     return f"{self.days_on} on, {self.days_off} off"

    def save(self, *args, **kwargs):
        if not self.duration:
            # Calculate duration if not provided
            start_datetime = timezone.make_aware(timezone.datetime.combine(timezone.now().date(), self.start_time))
            end_datetime = timezone.make_aware(timezone.datetime.combine(timezone.now().date(), self.end_time))
            if end_datetime <= start_datetime:
                end_datetime += timezone.timedelta(days=1)
            self.duration = end_datetime - start_datetime
        super().save(*args, **kwargs)


class Team(models.Model):
    MAX_TEAM_NAME_LENGTH = 50
    MIN_TEAM_NAME_LENGTH = 3

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='teams',
        #TODO CHECK WHER TO PUT NULL TRUE
        null=True,
    )

    name = models.CharField(
        max_length=MAX_TEAM_NAME_LENGTH,
        validators=[MinLengthValidator(MIN_TEAM_NAME_LENGTH)],
        blank=False,
        null=False,
    )

    manager = models.OneToOneField(
        Manager,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="team",
    )

    shift_pattern = models.ForeignKey(
        ShiftPattern,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='teams',
    )

    def __str__(self):
        return self.name


class Date(models.Model):
    date = models.DateField(
        unique=True,
        blank=False,
        null=False,
    )

# class ShiftAssignment(models.Model):
#     date = models.DateField()
#     shift_block = models.ForeignKey(ShiftBlock, on_delete=models.CASCADE, related_name='assignments')
#
#     class Meta:
#         # TODO make it unique for many companies
#         unique_together = ('date', 'shift_block',)
#
#     def __str__(self):
#         return f"{self.shift_block.pattern.name} - {self.date}"


