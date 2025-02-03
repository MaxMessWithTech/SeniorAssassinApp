from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=200)


class Participant(models.Model):
    name = models.CharField(max_length=200)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class Round(models.Model):
    index = models.IntegerField(default=0)


class Match(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE)
    team_2 = models.ForeignKey(Team, on_delete=models.CASCADE)

    start_date = 


