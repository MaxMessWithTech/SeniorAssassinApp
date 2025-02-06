from django.urls import path

from . import views

app_name = "assignments"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("home/<team_code>", views.home, name="home"),
]