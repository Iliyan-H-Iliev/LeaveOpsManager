from django import forms
from .models import ShiftPattern, ShiftBlock, Team
from django.forms.models import inlineformset_factory


class ShiftPatternForm(forms.ModelForm):

    # TODO is start_date is on week pattern should start from Monday!!!
    class Meta:
        model = ShiftPattern
        fields = ['name', 'description', 'rotation_weeks', 'start_date',]


class ShiftBlockForm(forms.ModelForm):
    CHOICES = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]

    selected_days = forms.MultipleChoiceField(
        choices=CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    days_on = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=28
    )

    days_off = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=28
    )

    class Meta:
        model = ShiftBlock
        fields = ["selected_days", 'days_on', 'days_off', 'start_time', 'end_time', "duration",'order']

    def clean(self):
        # TODO debug this
        cleaned_data = super().clean()
        selected_days = cleaned_data.get("selected_days")
        days_on = cleaned_data.get("days_on")
        days_off = cleaned_data.get("days_off")

        if not selected_days and (days_on is None or days_off is None):
            raise forms.ValidationError("You must specify either working days or a pattern (days on and days off).")

        if selected_days:
            working_days = [1 if str(i) in selected_days else 0 for i in range(1, 8)]
            self.instance.working_days = working_days

        elif days_on is not None and days_off is not None:
            working_days = [1] * days_on + [0] * days_off
            self.instance.working_days = working_days

        return cleaned_data


ShiftBlockFormSet = forms.inlineformset_factory(
    ShiftPattern, ShiftBlock,
    form=ShiftBlockForm,
    extra=2,
    can_delete=True
)


class TeamForm(forms.ModelForm):
    class Meta:
        # TODO add company field
        model = Team
        fields = ['name', 'manager', 'shift_pattern']
