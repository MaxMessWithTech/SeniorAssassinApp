from django.urls import path, re_path

from . import views

app_name = "assignments"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("home/<team_code>", views.home, name="home"),
    path("home/<team_code>/report-kill", views.reportKill, name="report-kill"),
    path("add-things", views.addThings, name="add-things"),
    path("assign-teams-in-round", views.assignTeamsInRound, name="assign-teams"),
    path("eliminate-participant", views.eliminateParticipant, name="eliminate-participant"),
    path("admin-control", views.adminControl, name="admin-control"),

    # path("participant-autocomplete/$", views.ParticipantAutocomplete.as_view(), name="participant-autocomplete"),
    # path("target-autocomplete/$", views.TargetAutocomplete.as_view(), name="target-autocomplete"),
    re_path(
        r'^target-autocomplete/$',
        views.TargetAutocomplete.as_view(),
        name='targetAutocomplete',
    ),
    re_path(
        r'^participant-autocomplete/$',
        views.ParticipantAutocomplete.as_view(),
        name='participantAutocomplete',
    ),
]