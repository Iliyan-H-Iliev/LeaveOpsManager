from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator, MaxValueValidator
from django.utils import timezone
from LeaveOpsManager.accounts.models import Manager, Company
from datetime import date, timedelta





class ShiftPattern(models.Model):
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 50
    MIN_ROTATION_WEEKS = 1
    MAX_ROTATION_WEEKS = 52

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='shift_patterns',
        null=True,
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generate_shift_assignments()

    def generate_shift_assignments(self):
        #TODO check if this is correct  and if it is working
        end_date = date(date.today().year + 1, 12, 31)
        current_date = self.start_date
        while current_date <= end_date:
            for block in self.blocks.all():
                working_days = block.working_days
                for i, day in enumerate(working_days):
                    if current_date > end_date:
                        break
                    if day == 1:  # Only create assignments for working days
                        for team in self.teams.all():
                            ShiftAssignment.objects.get_or_create(
                                date=current_date,
                                shift_block=block,
                            )
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


class ShiftAssignment(models.Model):
    date = models.DateField()
    shift_block = models.ForeignKey(ShiftBlock, on_delete=models.CASCADE, related_name='assignments')

    class Meta:
        # TODO make it unique for many companies
        unique_together = ('date', 'shift_block',)

    def __str__(self):
        return f"{self.team.name} - {self.shift_block.pattern.name} - {self.date}"
