from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import loader
from django.urls import reverse
from django.utils import timezone
import datetime
from django.db.models import Q

from assignments.models import Team, Participant, Round, Target

import csv
import assignments.handleCSV as handleCSV
from dal import autocomplete
import random


def getCurRound() -> Round:
	rounds = Round.objects.all()

	current_round = None
	for round in rounds: 
		if round.start_date <= timezone.now() and round.end_date > timezone.now():
			return round

	return None


def index(request):
	return HttpResponseRedirect(reverse("assignments:login"))

def login(request):
	if request.method == 'GET':
		template = loader.get_template("assignments/login.html")
		context = {
			# "latest_question_list": latest_question_list,
		}
		return HttpResponse(template.render(context, request))

	try:
		print(request.POST)
		team = Team.objects.get(viewing_code=request.POST["code"])
	except (KeyError, Team.DoesNotExist):
		# Redisplay the question voting form.
		return render(
			request,
			"assignments/login.html",
			{
				"error_message": "Invalid Code."
			},
		)
	else:
		
		# Always return an HttpResponseRedirect after successfully dealing
		# with POST data. This prevents data from being posted twice if a
		# user hits the Back button.
		return HttpResponseRedirect(reverse("assignments:home", args=(team.viewing_code,)))

def home(request, team_code):
	# latest_question_list = Question.objects.order_by("-pub_date")[:5]
	
	try:
		team = Team.objects.get(viewing_code=team_code)

	except (KeyError, Team.DoesNotExist):
		# Redisplay the question voting form.
		return HttpResponseRedirect(reverse("assignments:login"))
	
	else:
		current_round = getCurRound()
		current_round_index = current_round.index

		cur_round_targets = Target.objects.filter(round = current_round).filter(prosecuting_team = team)

		if len(cur_round_targets) != 1:
			print(f"Invalid number of targets!! Currently has {cur_round_targets}")

		cur_target = cur_round_targets[0]

		target_participant_objs = Participant.objects.filter(team=cur_target.target_team)
		
		target_participants = list()

		for p in target_participant_objs:
			target_participants.append(p.name)

		# Remaining Team Members
		remainingMembersObjs = Participant.objects.filter(team=team).filter(round_eliminated=False).filter(eliminated_permanently=False)
		
		remainingMembers = list()
		for p in remainingMembersObjs:
			remainingMembers.append(p.name)

		template = loader.get_template("assignments/home.html")
		context = {
			'team_code': team.viewing_code,
			'team_name': team.name,
			'current_round_index': current_round_index,
			'target_participants': ','.join(target_participants),
			'target_name': cur_target.target_team.name,
			'remaining_members': ','.join(remainingMembers)
		}
		return HttpResponse(template.render(context, request))


@login_required
def assignTeamsInRound(request):
	if request.method != 'POST':
		return HttpResponseBadRequest("Must be a POST request!")
	
	if "round_num" not in request.POST:
		return HttpResponseBadRequest("missing round_num param!")
	if "start_date" not in request.POST:
		return HttpResponseBadRequest("missing start_date param!")
	if "end_date" not in request.POST:
		return HttpResponseBadRequest("missing end_date param!")
	
	roundNum = int(request.POST["round_num"])
	startDate = datetime.datetime.fromisoformat(request.POST["start_date"])
	endDate = datetime.datetime.fromisoformat(request.POST["end_date"])

	existingRounds = Round.objects.filter(index=roundNum)

	if len(existingRounds) != 0:
		for oldRound in existingRounds:
			oldRound.delete()

	round = Round(index=roundNum, start_date=startDate, end_date=endDate)
	round.save()
	
	# Make random assignments
	teams = Team.objects.all()

	for team in teams:
		pairedID = random.randint(1, len(teams))
		targetTeam = Team.objects.filter(id=pairedID).first()

		target = Target(
			round=round, 
			target_team=targetTeam, 
			prosecuting_team=team, 
			eliminations=0
		)
		target.save()
		

	return HttpResponseRedirect(reverse("assignments:admin-control"))


class ParticipantAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Participant.objects.none()

        qs = Participant.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


@login_required
def adminControl(request):
	try:
		current_round = getCurRound()
		current_round_index = current_round.index

		round_elims = Participant.objects.filter(round_eliminated=True, eliminated_permanently=False)
		perm_elims = Participant.objects.filter(eliminated_permanently=True)
		remaining = Participant.objects.filter(round_eliminated=False, eliminated_permanently=False)
	except:
		current_round = None
		current_round_index = -1

		round_elims = []
		perm_elims = []
		remaining = []
	
	template = loader.get_template("assignments/adminControl.html")
	context = {
		'current_round_index': current_round_index,
		'eliminated_this_round': len(round_elims),
		'eliminated_permanently': len(perm_elims),
		'remaining': len(remaining)
	}
	return HttpResponse(template.render(context, request))


@login_required
def addThings(request):
	data = 	list()
	with open('SeniorAssassinTeams.csv', mode ='r') as file:
		csvFile = csv.reader(file)

		# Collect Data
		for lines in csvFile:
			data.append(lines)

	for row in data[1:]:
		id = handleCSV.getIDFromCSV(data[0], row)
		name = handleCSV.getNameFromCSV(data[0], row)
		teammates = handleCSV.getTeammatesFromCSV(data[0], row)
		valid = handleCSV.checkIfTeamValid(id, name, teammates)

		# Stop going through this team if it isn't valid
		if not valid:
			continue
		# print(f"Team '{name}' of ID {id}; People: {teammates}; valid: {valid}")

		existingTeam = Team.objects.filter(id=id).first()
		if existingTeam is not None:
			existingTeam.name = name
			existingTeam.save()
			
			# existingParticipants = Participant.objects.filter(team=existingTeam)

			continue

		team = Team(id=id, name=name)
		team.save()
		for name in teammates:
			if len(name) == 0:
				continue

			person = Participant(name=name, team=team)
			person.save()



	print("Added all data from the CSV")
	return HttpResponse("Added all data from the CSV")
