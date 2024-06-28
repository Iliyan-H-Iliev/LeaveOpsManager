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
            shift_pattern = form.save(commit=False)
            shift_pattern.company = request.user.get_company
            # Check if a ShiftPattern with the same company and name already exists
            if ShiftPattern.objects.filter(company=shift_pattern.company, name=shift_pattern.name).exists():
                form.add_error('name', 'Shift pattern with this name already exists for your company.')
                return render(request, 'shiftpattern_form.html', {'form': form, 'formset': formset})
            shift_pattern.save()
            shift_blocks = formset.save(commit=False)
            for block in shift_blocks:
                block.pattern = shift_pattern
                block.save()
            formset.save_m2m()
            shift_pattern.generate_shift_working_dates()
            return redirect('shiftpattern_list')
        return render(request, 'shiftpattern_form.html', {'form': form, 'formset': formset})


class ShiftPatternListView(View):
    def get(self, request):
        shift_patterns = ShiftPattern.objects.filter(company=request.user.get_company)
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