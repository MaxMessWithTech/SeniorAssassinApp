from django.db import models
import random
import string
import django
from smart_selects.db_fields import ChainedForeignKey


class Team(models.Model):
    id = models.IntegerField(default=0, primary_key=True)
    name = models.CharField(max_length=200)
    eliminated = models.BooleanField(default=False)

    def generate_viewing_code() -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    viewing_code = models.CharField(max_length=8, default=generate_viewing_code, unique=True)

    def __str__(self):
        return f"{self.id}-{self.name}"


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
        return f"Round {self.round.index} target of {self.target_team} by {self.prosecuting_team.name}"


class Kill(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='target', null=True)
    
    elimed_participant = models.ForeignKey(Participant, on_delete=models.CASCADE,  related_name='elimed_participant',  null=True)
    eliminator = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='eliminator', null=True)

    date = models.DateField(default=django.utils.timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:
            # This code only happens if the objects is
            # not in the database yet. Otherwise it would a have pk
            
            self.target.eliminations += 1
            self.target.save()

            self.elimed_participant.round_eliminated = True
            self.elimed_participant.save()


        super(Kill, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.elimed_participant.name} killed by {self.eliminator.name} on {self.date.strftime('%A, %B %d')}"
