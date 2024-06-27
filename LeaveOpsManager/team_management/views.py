from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.views import View
from .models import ShiftPattern, Team
from .forms import ShiftPatternForm, ShiftBlockFormSet, TeamForm

UserModel = get_user_model()


class ShiftPatternCreateView(View):
    def get(self, request):
        form = ShiftPatternForm()
        formset = ShiftBlockFormSet()
        return render(request, 'shiftpattern_form.html', {'form': form, 'formset': formset})

    def post(self, request):
        form = ShiftPatternForm(request.POST)
        formset = ShiftBlockFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            shift_pattern = form.save()
            shift_blocks = formset.save(commit=False)
            for block in shift_blocks:
                block.pattern = shift_pattern
                block.save()
            formset.save_m2m()
            return redirect('shiftpattern_list')
        return render(request, 'shiftpattern_form.html', {'form': form, 'formset': formset})


class ShiftPatternListView(View):
    def get(self, request):
        shift_patterns = ShiftPattern.objects.all()
        return render(request, 'shiftpattern_list.html', {'shift_patterns': shift_patterns})


class TeamCreateView(View):
    def get(self, request):
        form = TeamForm()
        return render(request, 'team_form.html', {'form': form})

    def post(self, request):
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('team_list')
        return render(request, 'team_form.html', {'form': form})

class TeamListView(View):
    def get(self, request):
        teams = Team.objects.all()
        return render(request, 'team_list.html', {'teams': teams})