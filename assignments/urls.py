from django.urls import path, re_path
from django.shortcuts import redirect

from . import views

app_name = "assignments"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("home/<team_code>", views.home, name="home"),
    path("status/", views.gameStatus, name="status"),
    path("vote/<team_code>/<issue_id>", views.vote, name="vote"),

    path("home/<team_code>/report-kill", views.reportKill, name="report-kill"),
    path("assign-teams-in-round", views.createRound, name="assign-teams"),
    path("add-things", views.addThings, name="add-things"),
    path("eliminate-participant", views.eliminateParticipant, name="eliminate-participant"),
    path("cleanup_round", views.cleanup_round, name="cleanup_round"),
    path("create_purge", views.create_purge, name="create_purge"),
    path("admin-control", views.adminControl, name="admin-control"),
    path("accounts/login/", views.admin_login_view, name="admin-login"),
]

def custom_404(request, exception):
    return redirect('/')


handler404 = custom_404
