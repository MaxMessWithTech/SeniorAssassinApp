from django.db import models
import random
import string
import django
from smart_selects.db_fields import ChainedForeignKey
import math


class Team(models.Model):
    id = models.IntegerField(default=0, primary_key=True)
    name = models.CharField(max_length=200)

    eliminated = models.BooleanField(default=False)
    eliminated_date=models.DateField(null=True, blank=True)

    def generate_viewing_code() -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    viewing_code = models.CharField(max_length=8, default=generate_viewing_code, unique=True)
    
    def get_round_elimed(self):
        filtered_p = list()
        for p in self.participants.all():
            if p.round_eliminated is True and p.eliminated_permanently is False:
                filtered_p.append(p)
        
        return filtered_p
    
    def get_round_elimed_count(self):
        return len(self.get_round_elimed())
    
    def get_perm_elimed(self):
        filtered_p = list()
        for p in self.participants.all():
            if p.eliminated_permanently is True:
                filtered_p.append(p)
        
        return filtered_p
    
    def get_perm_elimed_count(self):
        return len(self.get_perm_elimed())
    
    def get_remaining(self):
        filtered_p = list()
        for p in self.participants.all():
            if p.round_eliminated is False and p.eliminated_permanently is False:
                filtered_p.append(p)
        
        return filtered_p
    
    def get_remaining_count(self):
        return len(self.get_remaining())
    
    def get_participants(self):
        return self.participants.all()
    
    def get_participants_first_name(self):
        filtered_p = list()
        for p in self.participants.all():
            if p.round_eliminated is False and p.eliminated_permanently is False:
                filtered_p.append(p.name.split(" ")[0])

        return ", ".join(filtered_p)


    def __str__(self):
        return f"{self.id}-{self.name}"


class Participant(models.Model):
    name = models.CharField(max_length=200)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="participants")

    # A participant can be eliminated in a round and then revived 
    # if their team eliminates 3 people on the team they're matched against
    round_eliminated = models.BooleanField(default=False)
    eliminated_permanently = models.BooleanField(default=False)

    def get_color(self):
        if self.eliminated_permanently:
            return "#DC4C64"
        
        if self.round_eliminated:
            return "#E4A11B"
        
        return "#14A44D"

    def is_eliminated(self):
        return self.round_eliminated or self.eliminated_permanently

    def __str__(self):
        if self.team is None:
            return f"{self.name} from team NO TEAM"
        
        return f"{self.name} from team '{self.team.name}'"


class Round(models.Model):
    index = models.IntegerField(default=0)

    start_date = models.DateTimeField("Date Round Starts")
    end_date = models.DateTimeField("Date Round Ends")

    completed = models.BooleanField(default=False)

    def get_start_date_str(self):
        return self.start_date.strftime("%m/%d")

    def __str__(self):
        return f"Round {self.index}"


class Target(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='targets')
    target_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='targets')
    prosecuting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='prosecuting_targets')
    
    eliminations = models.IntegerField(default=0)

    def __str__(self):
        return f"Round {self.round.index} target of {self.target_team.name} by {self.prosecuting_team.name}"


class Kill(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='target', null=True)
    
    elimed_participant = models.ForeignKey(Participant, on_delete=models.CASCADE,  related_name='eliminations',  null=True)
    eliminator = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='kills', null=True)

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


class RuleSuspension(models.Model):
    type = models.CharField(max_length=100)
    rules_suspended = models.TextField()
    notification_time = models.DateTimeField()
    start_time = models.DateField()
    end_time = models.DateField()


class Issue(models.Model):
    label = models.CharField(max_length=100)
    description = models.CharField(max_length=400)

    team_vote = models.BooleanField(default=False)

    def get_for_votes(self):
        votes = self.votes.filter(in_favor=True)

        count = 0

        for vote in votes:
            if self.team_vote and not vote.team.eliminated:
                count += 1
                continue

            if not vote.participant.is_eliminated():
                count += 1

        return count
    
    def get_against_votes(self):
        votes = self.votes.filter(in_favor=False)

        count = 0

        for vote in votes:
            if self.team_vote and not vote.team.eliminated:
                count += 1
                continue

            if not vote.participant.is_eliminated():
                count += 1

        return count

    def get_delta(self):
        for_votes = self.get_for_votes()
        against_votes = self.get_against_votes()

        return for_votes-against_votes

    def did_pass(self):

        majority = 0

        if self.team_vote:
            majority = math.floor(len(Team.objects.filter(is_eliminated=False)) / 2)
        else:
            majority = math.floor(len(
                Participant.objects.filter(round_eliminated=False).filter(eliminated_permanently=False)
            ))

        for_votes = self.get_for_votes()

        return for_votes >= majority


class Vote(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='votes', null=True)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='votes', null=True)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='votes', null=True)

    in_favor = models.BooleanField(default=False)
