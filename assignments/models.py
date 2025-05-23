from django.db import models
import random
import string
import django
from smart_selects.db_fields import ChainedForeignKey
import math
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Team(models.Model):
	id = models.IntegerField(default=0, primary_key=True)
	name = models.CharField(max_length=200)

	eliminated = models.BooleanField(default=False)
	eliminated_date=models.DateField(null=True, blank=True)

	history = HistoricalRecords()


	def generate_viewing_code() -> str:
		return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
	
	viewing_code = models.CharField(max_length=8, default=generate_viewing_code, unique=True)
	

	def get_cur_targets(self) -> list:
		return self.prosecuting_targets.filter(round=getCurRound())

	# Get participants who have been round eliminated
	def get_round_elimed(self) -> list:
		if self.eliminated:
			return []

		filtered_p = list()
		for p in self.participants.all():
			if p.round_eliminated is True and p.eliminated_permanently is False:
				filtered_p.append(p)
		
		return filtered_p
	
	# Get # of participants who have been round eliminated
	def get_round_elimed_count(self) -> int:
		if self.eliminated:
			return -1
		
		return len(self.get_round_elimed())
	
	# Get participants who have been permanently eliminated
	def get_perm_elimed(self) -> list:
		if self.eliminated:
			return []
		
		filtered_p = list()
		for p in self.participants.all():
			if p.eliminated_permanently is True:
				filtered_p.append(p)
		
		return filtered_p
	
	# Get # of participants who have been permanently eliminated
	def get_perm_elimed_count(self) -> int:
		if self.eliminated:
			return -1
		
		return len(self.get_perm_elimed())
	
	# Get remaining participants
	def get_remaining(self) -> list:
		if self.eliminated:
			return []
		
		filtered_p = list()
		for p in self.participants.all():
			if p.round_eliminated is False and p.eliminated_permanently is False:
				filtered_p.append(p)
		
		return filtered_p
	
	# Get # of remaining participants
	def get_remaining_count(self) -> int:
		if self.eliminated:
			return -1
		
		return len(self.get_remaining())
	
	# Get all participants
	def get_participants(self) -> list:
		return self.participants.all()
	
	# Get all participant's first names
	def get_participants_first_name(self) -> str:
		filtered_p = list()
		for p in self.participants.all():
			if p.round_eliminated is False and p.eliminated_permanently is False:
				filtered_p.append(p.name.split(" ")[0])

		return ", ".join(filtered_p)

	# Get # of kills this round
	def get_round_kills(self) -> list:
		try:
			kills = list()
			for target in self.get_cur_targets().all():
				for kill in target.kills.all():

					kills.append(kill.elimed_participant)
			
			return kills
		except:
			return []

	# Get # of kills this round
	def get_round_kills_count(self) -> int:
		if self.eliminated:
			return -1

		try:
			kills = self.get_round_kills()
			return len(kills)
		except:
			return -1
		
	
	# Get # of kills during the entire game
	def get_total_kills_count(self) -> int:
		counter = 0

		targets = self.prosecuting_targets.all()
		
		for target in targets:
			counter += len(target.kills.all())
		
		return counter


	def revive(self):
		# Revive team members eliminated this round
		ps = self.get_round_elimed()

		# For person in people
		for p in ps:
			p.round_eliminated = False
			p.save()


	def try_revive(self) -> bool:
		if self.get_round_kills_count() >= getCurRound().min_revive_kill_count:
			self.revive()
			return True
		
		target = self.get_cur_targets().first()
		target_team = target.target_team
		i = target_team.get_remaining_count() + target_team.get_round_elimed_count()
		
		# Met minium of 2/3 of team eliminated instead of the min_revive_kill_count
		if self.get_round_kills_count() >= math.ceil(i * (2/3)):
			self.revive()
			return True
			
		

		if self.get_round_kills_count() >= getCurRound().min_progression_kill_count:
			return False
		
		# Permanently eliminate all round eliminated team members
		ps = self.get_round_elimed()

		for p in ps:
			p.eliminated_permanently = True
			p.save()

		if self.get_remaining_count() == 0:
			self.eliminate()

		return False


	# Will this team progress from a the current round
	def will_progress_in_round(self) -> bool:
		cur_round = getCurRound()

		if cur_round is None:
			return False

		if self.pro_overrides.filter(round=cur_round).first():
			return True
		
		if self.get_round_kills_count() >= cur_round.min_progression_kill_count:
			return True
		
		print(f"Team {self.name} will not progress because {self.get_round_kills_count()} < {cur_round.min_progression_kill_count}")
		
		return False
	

	def eliminate(self):
		self.eliminated = True
		self.eliminated_date = timezone.now()
		self.save()

		for p in self.get_participants():
			p.round_eliminated = True
			p.eliminated_permanently = True
			p.save()

		

	def __str__(self):
		return f"{self.id}-{self.name}"


class Participant(models.Model):
	name = models.CharField(max_length=200)
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="participants")

	history = HistoricalRecords()

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

	def __repr__(self):
		return f"{self.name}"


class Round(models.Model):
	index = models.IntegerField(default=0)

	start_date = models.DateTimeField("Date Round Starts")
	end_date = models.DateTimeField("Date Round Ends")

	min_progression_kill_count = models.IntegerField(default=0)
	min_revive_kill_count = models.IntegerField(default=2)

	completed = models.BooleanField(default=False)

	history = HistoricalRecords()

	def get_start_date_str(self):
		return self.start_date.strftime("%m/%d")

	def __str__(self):
		return f"Round {self.index}"


class Target(models.Model):
	round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='targets')
	target_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='targets')
	prosecuting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='prosecuting_targets')
	
	eliminations = models.IntegerField(default=0)

	history = HistoricalRecords()


	def __str__(self):
		return f"Round {self.round.index} target of {self.target_team.name} by {self.prosecuting_team.name}"


class Kill(models.Model):
	target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name='kills', null=True)
	
	elimed_participant = models.ForeignKey(Participant, on_delete=models.CASCADE,  related_name='eliminations',  null=True)
	eliminator = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='kills', null=True)

	date = models.DateField(default=django.utils.timezone.now)

	video_link = models.URLField(max_length=200, null=True)

	history = HistoricalRecords()


	def get_round(self):
		return self.target.round

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
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()

	history = HistoricalRecords()


class Issue(models.Model):
	label = models.CharField(max_length=100)
	description = models.TextField()

	team_vote = models.BooleanField(default=False)

	closed = models.BooleanField(default=False)

	history = HistoricalRecords()

	def get_for_votes(self):
		votes = self.votes.filter(in_favor=True)

		count = 0

		for vote in votes:
			if self.team_vote and not vote.team.eliminated:
				count += 1
				continue

			elif not vote.participant.is_eliminated():
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

	def get_majority(self):
		majority = 0

		if self.team_vote:
			majority = math.floor(len(Team.objects.filter(eliminated=False)) / 2)
		else:
			majority = math.floor(len(
				Participant.objects.filter(round_eliminated=False).filter(eliminated_permanently=False)
			) / 2)

		return majority

	def did_pass(self):

		majority = self.get_majority()

		for_votes = self.get_for_votes()

		return for_votes >= majority


class Vote(models.Model):
	issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='votes')

	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='votes')
	participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='votes', null=True)

	in_favor = models.BooleanField(default=False)

	history = HistoricalRecords()


class ProgressionOverride(models.Model):
	id = models.IntegerField(primary_key=True)
	round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='pro_overrides')
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='pro_overrides')

	issued_date = models.DateTimeField(default=django.utils.timezone.now)

	history = HistoricalRecords()


	def __str__(self):
		return f"Round {self.round.index} Override for {self.team.name}"


def getCurRound() -> Round:
	rounds = Round.objects.filter(completed = False)

	for round in rounds: 
		if round.start_date <= timezone.now() and round.end_date > timezone.now():
			return round
	
	return None