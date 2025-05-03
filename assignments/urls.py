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
    path("add-things", views.addThings, name="add-things"),
    path("eliminate-participant", views.eliminateParticipant, name="eliminate-participant"),
    path("add_drive_url", views.add_drive_url, name="add_drive_url"),
    path("cleanup_round", views.cleanup_round, name="cleanup_round"),
    path("create_purge", views.create_purge, name="create_purge"),
    
    path("create-round/<prev_round_id>", views.createRoundPage, name="create-round"),
    path("create-round-post/", views.createRoundPost, name="create-round-post"),

    path("admin-control", views.adminControl, name="admin-control"),

    path("accounts/login/", views.admin_login_view, name="admin-login"),

    path("revertThingsFromToday/", views.revertThingsFromToday, name="revert")
]

def custom_404(request, exception):
    return redirect('/')


handler404 = custom_404
