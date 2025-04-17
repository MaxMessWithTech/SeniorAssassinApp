from django.utils import timezone
import datetime
from assignments.models import Team, Participant, Round, Target, Kill, RuleSuspension, Issue, Vote
import random


# Makes 1 to 1 pairings for a round
def make_direct_pairings(round:Round):
	teams = Team.objects.filter(eliminated=False)
	all_ids = list()

	for team in teams:
		all_ids.append(team.id)

	assignedIDs = list()

	for team in teams:
		while True:
			pairedID = random.randint(0, len(all_ids) - 1)
			if pairedID in assignedIDs or all_ids[pairedID] == team.id:
				continue


			targetTeam = Team.objects.filter(id=all_ids[pairedID]).first()

			target = Target(
				round=round, 
				target_team=targetTeam, 
				prosecuting_team=team, 
				eliminations=0
			)
			target.save()

			assignedIDs.append(pairedID)
			break


# Helper Method for make_multi_pairings
def make_layer_pairing(round:Round, teams:list[Team]) -> list[Target]:
	teams = teams.copy()

	pairings = list()

	while len(teams) > 0:
		pairings.append(
			teams.pop( index = random.randint( len( teams ) ) )
		)

	targets = list()

	for i in range( len(pairings) - 1 ):

		target = Target(
			round = round, 
			target_team = pairings[i], 
			prosecuting_team = pairings[i + 1], 
			eliminations = 0
		)
		target.save()

		targets.append(target)

	return targets


# Allows for each team to receive multiple pairings
def make_multi_pairings(round:Round, depth:int):
	teams_filter = Team.objects.filter(eliminated=False)

	teams = list()
	for team in teams_filter:
		teams.append(team)

	pair_depth = list()

	for i in depth:
		pair_depth.append(make_layer_pairing(round, teams))


# Helper Method
def create_new_round(round_num, start_date, end_date):	
	roundNum = int(round_num)
	startDate = datetime.datetime.fromisoformat(start_date)
	endDate = datetime.datetime.fromisoformat(end_date)

	existingRounds = Round.objects.filter(index=roundNum)

	if len(existingRounds) != 0:
		for oldRound in existingRounds:
			oldRound.delete()

	round = Round(index=roundNum, start_date=startDate, end_date=endDate)
	round.save()
	
	# Make random assignments
	make_direct_pairings(round=round)