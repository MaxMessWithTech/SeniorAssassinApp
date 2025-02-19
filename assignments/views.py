from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import loader
from django.urls import reverse
from django.utils import timezone
import datetime
from django.db.models import Q
from django.forms.models import model_to_dict
import assignments.forms

from assignments.models import Team, Participant, Round, Target, Kill

import csv
import assignments.handleCSV as handleCSV
from dal import autocomplete
import random


def getCurRound() -> Round:
	rounds = Round.objects.all()

	for round in rounds: 
		if round.start_date <= timezone.now() and round.end_date > timezone.now():
			return round
	return None


def convertQueryToNameList(query) -> list:
	out = list()

	for p in query:
		out.append(p.name)

	if len(out) == 0:
		out.append("NONE")
	
	return out


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

		current_round = getCurRound()
		current_round_index = current_round.index

	except (KeyError, Team.DoesNotExist):
		# Redisplay the question voting form.
		return HttpResponseRedirect(reverse("assignments:login"))
	
	except (AttributeError):
		dneTemplate = loader.get_template("assignments/roundDNE.html")

		return HttpResponse(dneTemplate.render({}, request))

	else:

		cur_round_targets = Target.objects.filter(round = current_round).filter(prosecuting_team = team)

		if len(cur_round_targets) != 1:
			print(f"Invalid number of targets!! Currently has {cur_round_targets}")

		cur_target = cur_round_targets[0]

		# Get target participants
		target_participant_objs = Participant.objects.filter(team=cur_target.target_team).filter(eliminated_permanently=False)
		target_participants = convertQueryToNameList(target_participant_objs)

		# Get Eliminated Targets
		eliminated_targets = target_participant_objs.filter(round_eliminated=True)
		elimed_targets = convertQueryToNameList(eliminated_targets)


		# Get Remaining Team Members
		remainingMembersObjs = Participant.objects.filter(team=team).filter(round_eliminated=False).filter(eliminated_permanently=False)
		remainingMembers = convertQueryToNameList(remainingMembersObjs)

		# Get Round Elimed Team Members
		roundElimedMembersObjs = Participant.objects.filter(team=team).filter(round_eliminated=True).filter(eliminated_permanently=False)
		roundElimedTeam = convertQueryToNameList(roundElimedMembersObjs)

		# Get Perm Elimed Team Members
		permElimedObjs = Participant.objects.filter(team=team).filter(eliminated_permanently=True)
		permElimedTeam = convertQueryToNameList(permElimedObjs)

		

		notifications = list()

		kills = Kill.objects.filter(target=cur_target)
		
		for kill in kills:
			notifications.append(str(kill))
		

		template = loader.get_template("assignments/home.html")
		context = {
			'team_code': team.viewing_code,
			'team_name': team.name,
			'current_round_index': current_round_index,
			'cur_round_start': current_round.start_date,
			'cur_round_end': current_round.end_date,
			'target_participants': ', '.join(target_participants),
			'elimed_targets':  ', '.join(elimed_targets),
			'target_name': cur_target.target_team.name,
			'notifications': notifications,
			'remaining_members': ', '.join(remainingMembers),
			'roundElimedTeam': ', '.join(roundElimedTeam),
			'permElimedTeam': ', '.join(permElimedTeam),
			'cur_target':cur_target

		}
		return HttpResponse(template.render(context, request))

def reportKill(request, team_code):
	template = loader.get_template("assignments/home.html")
	context = {
		'team_code': team_code,
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
	teams = Team.objects.filter(eliminated=False)

	assignedIDs = list()

	for team in teams:
		while True:
			pairedID = random.randint(1, len(teams))
			if pairedID in assignedIDs:
				continue


			targetTeam = Team.objects.filter(id=pairedID).first()

			target = Target(
				round=round, 
				target_team=targetTeam, 
				prosecuting_team=team, 
				eliminations=0
			)
			target.save()

			assignedIDs.append(pairedID)
			break
		

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
	except Exception as e:
		print(e)
		current_round = None
		current_round_index = -1

		round_elims = []
		perm_elims = []
		remaining = []
	
	round_targets = Target.objects.filter(round=getCurRound())
	round_target_list = list()
	for target in round_targets:
		round_target_list.append(model_to_dict(target))


	all_teams = Team.objects.all()
	team_list = list()
	for team in all_teams:
		team_list.append(model_to_dict(team))

	participants = Participant.objects.all()
	participant_list = list()
	for participant in participants:
		participant_list.append(model_to_dict(participant))

	template = loader.get_template("assignments/adminControl.html")
	context = {
		'current_round_index': current_round_index,
		'eliminated_this_round': len(round_elims),
		'eliminated_permanently': len(perm_elims),
		'remaining': len(remaining),
		'round_targets': round_targets,
		'round_targets_ser': round_target_list,
		'all_teams': team_list,
		'participants': participant_list
	}
	return HttpResponse(template.render(context, request))


@login_required
def eliminateParticipant(request):
	if request.method != 'POST':
		return HttpResponseBadRequest("Must be a POST request!")
	
	"""
	POST PARAMS
	target_id, elimed_participant_id, eliminator_id, date
	"""
	
	if "target_id" not in request.POST:
		return HttpResponseBadRequest("missing target ID param!")
	if "elimed_participant_id" not in request.POST:
		return HttpResponseBadRequest("missing elimed_participant ID param!")
	if "eliminator_id" not in request.POST:
		return HttpResponseBadRequest("missing eliminator ID param!")
	
	target = get_object_or_404(Target, id=int(request.POST["target_id"]))

	elimed_participant = get_object_or_404(
		Participant, id=int(request.POST["elimed_participant_id"])
	)

	eliminator = get_object_or_404(
		Participant, id=int(request.POST["eliminator_id"])
	)
	
	kill = Kill(
		target = target,
		elimed_participant = elimed_participant,
		eliminator = eliminator,
		date = datetime.datetime.fromisoformat(request.POST["date"])
	)

	kill.save()
	
	elimed_participant.round_eliminated = True
	elimed_participant.save()

	return HttpResponseRedirect(reverse("assignments:admin-control"))


class ParticipantAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated:
			return Participant.objects.none()
		qs = Participant.objects.all()
		if self.q:
			qs = qs.filter(name__istartswith=self.q) # Adjust filter as needed
		return qs
	

class TargetAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		if not self.request.user.is_authenticated:
			return Target.objects.none()
		qs = Target.objects.all()
		if self.q:
			qs = qs.filter(name__istartswith=self.q) # Adjust filter as needed
		return qs



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
