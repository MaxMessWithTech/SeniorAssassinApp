from django.db import models
import random
import string


class Team(models.Model):
    name = models.CharField(max_length=200)
    eliminated = models.BooleanField(default=False)

    def generate_viewing_code() -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    viewing_code = models.CharField(max_length=8, default=generate_viewing_code, unique=True)

    def __str__(self):
        return f"{self.name}"


class Participant(models.Model):
    name = models.CharField(max_length=200)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    # A participant can be eliminated in a round and then revived 
    # if their team eliminates 3 people on the team they're matched against
    round_eliminated = models.BooleanField(default=False)
    eliminated_permanently = models.BooleanField(default=False)

    def __str__(self):
        if self.team is None:
            return f"{self.name} from team NO TEAM"
        
        return f"{self.name} from team '{self.team.name}'"


class Round(models.Model):
    index = models.IntegerField(default=0)

    start_date = models.DateTimeField("Date Round Starts")
    end_date = models.DateTimeField("Date Round Ends")

    def __str__(self):
        return f"Round {self.index}"


class Target(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='match_round')
    target_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='target_team')
    prosecuting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='prosecuting_team')
    
    eliminations = models.IntegerField(default=0)

    def __str__(self):
        return f"Round {self.round.index} target of {self.target_team.name} by {self.prosecuting_team.name}"


