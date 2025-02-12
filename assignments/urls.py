from django.urls import path

from . import views

app_name = "assignments"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("home/<team_code>", views.home, name="home"),
    path("add-things", views.addThings, name="add-things"),
    path("assign-teams-in-round", views.assignTeamsInRound, name="assign-teams"),
    path("admin-control", views.adminControl, name="admin-control"),
]