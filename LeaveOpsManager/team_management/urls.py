from django.urls import path
from .views import ShiftPatternCreateView, ShiftPatternListView, TeamCreateView, TeamListView

urlpatterns = [
    path('shiftpatterns/', ShiftPatternListView.as_view(), name='shiftpattern_list'),
    path('shiftpatterns/new/', ShiftPatternCreateView.as_view(), name='shiftpattern_create'),
    path('teams/', TeamListView.as_view(), name='team_list'),
    path('teams/new/', TeamCreateView.as_view(), name='team_create'),
]