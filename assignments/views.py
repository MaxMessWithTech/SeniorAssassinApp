from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone
import datetime
from django.db.models import Q
from django.forms.models import model_to_dict
import assignments.forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from assignments.models import Team, Participant, Round, Target, Kill, RuleSuspension, Issue, Vote

import csv
import assignments.handleCSV as handleCSV
from dal import autocomplete
import random

from assignments.notifications import Notifications

from assignments import roundManager


def getCurRound() -> Round:
	rounds = Round.objects.filter(completed = False)

	for round in rounds: 
		if round.start_date <= timezone.now() and round.end_date > timezone.now():
			return round
	
	return None

def getNextRound() -> Round:
	rounds = Round.objects.filter(completed = False).order_by("start_date")

	for round in rounds: 
		if round.end_date > timezone.now():
			return round
	
	return Round.objects.first()


def getCurRuleSuspension () -> RuleSuspension:
	ruleSuspensions = RuleSuspension.objects.all()
	print(ruleSuspensions)
	print(timezone.now())

	for r in ruleSuspensions: 
		print(r.end_time > timezone.now(), r.end_time, timezone.now())
		if r.notification_time <= timezone.now() and r.end_time > timezone.now():
			return r
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

def login_view(request):
	# Check if admin is logging in, if so, redirect to admin-control
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse("assignments:admin-control"))


	if request.method == 'GET':
		template = loader.get_template("assignments/login.html")
		context = {
			# "latest_question_list": latest_question_list,
		}
		return HttpResponse(template.render(context, request))

	try:
		# print(request.POST)
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
	try:
		team = Team.objects.get(viewing_code=team_code)

		current_round = getCurRound()
		current_round_index = current_round.index

	except (KeyError, Team.DoesNotExist):
		# Redisplay the question voting form.
		return HttpResponseRedirect(reverse("assignments:login"))
	
	except (AttributeError):
		dneTemplate = loader.get_template("assignments/roundDNE.html")

		return HttpResponse(dneTemplate.render({'nextRound': getNextRound()}, request))

	if team.eliminated:
		errorTemplate = loader.get_template("assignments/error.html")
		return HttpResponse(
			errorTemplate.render({'message': "Your team has been eliminated from the game!"}, request)
		)

	cur_round_targets = Target.objects.filter(round = current_round).filter(prosecuting_team = team)

	cur_targets = cur_round_targets

	# NOTIFICATIONS

	notifications = Notifications()
	for target in cur_targets:
		notifications.addKills( kills=Kill.objects.filter(target=target) )
		
	notifications.addIssues( issues = Issue.objects.filter(closed=False), team_code=team_code )
	notifications.addStatus()
	
	# RULE SUSPENSION
	ruleSuspension = getCurRuleSuspension()

	# TEMPLATE RETURN
	template = loader.get_template("assignments/home.html")
	context = {
		'team_code': team.viewing_code,
		'team_name': team.name,
		'current_round_index': current_round_index,
		'cur_round_start': current_round.start_date,
		'cur_round_end': current_round.end_date,

		'team': team,

		'notifications': notifications.get(),

		'cur_targets':cur_targets,
		'rule_suspension': ruleSuspension

	}
	return HttpResponse(template.render(context, request))

def reportKill(request, team_code):
	template = loader.get_template("assignments/home.html")
	context = {
		'team_code': team_code,
	}
	return HttpResponse(template.render(context, request))


def gameStatus(request):
	try:
		current_round = getCurRound()

		if current_round is None:
			current_round = getNextRound()
			
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
	
	round_targets = Target.objects.filter(round=current_round).order_by("id")
	round_target_list = list()
	for target in round_targets:
		round_target_list.append(model_to_dict(target))


	all_teams = Team.objects.filter(eliminated=False)
	team_list = list()
	for team in all_teams:
		team_list.append(model_to_dict(team))

	participants = Participant.objects.all()
	participant_list = list()
	for participant in participants:
		participant_list.append(model_to_dict(participant))

	kills = Kill.objects.all().order_by('date')
	round_kills = list()
	for kill in kills:
		print(kill.get_round(), current_round)
		if kill.get_round().index == current_round.index:
			round_kills.append(kill)

	print(kills)
	print(round_kills)

	template = loader.get_template("assignments/gameStatus.html")
	context = {
		'current_round': current_round,
		'current_round_index': current_round_index,
		'eliminated_this_round': len(round_elims),
		'eliminated_permanently': len(perm_elims),
		'remaining': len(remaining),
		'round_targets': round_targets,
		'round_targets_ser': round_target_list,
		'teams': all_teams,
		'team_list': team_list,
		'participants': participant_list,
		'round_kills': round_kills
	}
	return HttpResponse(template.render(context, request))

def vote(request, team_code, issue_id):
	if request.method == 'POST':
		print(request.POST)
		pID = int(request.POST["participant"])
		inFavor = False
		if "inFavor" in request.POST:
			inFavor = request.POST["inFavor"] == "on"

		participant = Participant.objects.filter(id=pID).first()

		vote = Vote(
			issue=Issue.objects.filter(id=issue_id).first(),
			team=participant.team,
			participant=participant,
			in_favor=inFavor
		)
		vote.save()

		return HttpResponseRedirect(reverse("assignments:home", args=(team_code,)))


	team = Team.objects.filter(viewing_code=team_code).first()
	participants = team.participants.all()
	issue = Issue.objects.filter(id=issue_id).first()

	p_list = list()

	for p in participants:
		if not issue.votes.filter(participant=p).first():
			p_list.append(p)



	template = loader.get_template("assignments/vote.html")
	context = {
		'team_code': team_code,
		'participants': p_list,
		'team': team,
		'issue':issue
	}
	return HttpResponse(template.render(context, request)) 


# ADMIN
# ADMIN
# ADMIN

def admin_login_view(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse("assignments:admin-control"))

	if request.method == 'GET':
		template = loader.get_template("admin_login.html")
		context = {
			# "latest_question_list": latest_question_list,
		}
		return HttpResponse(template.render(context, request))
	elif request.method == 'POST':
		username = request.POST["username"]
		password = request.POST["password"]
		
		user = authenticate(username=username, password=password)

		if user is None:
			# Redisplay the question voting form.
			return render(
				request,
				"admin_login.html",
				{
					"error_message": "Invalid credentials."
				},
			)
		
		login(request, user)
		return HttpResponseRedirect(reverse("assignments:admin-control"))


# URL "create-round-post"
@login_required(login_url="/accounts/login/")
def createRoundPost(request):
	if request.method != 'POST':
		return HttpResponseBadRequest("Must be a POST request!")
	
	if "prog_kills" not in request.POST:
		return HttpResponseBadRequest("missing prog_kills param!")
	if "rev_kills" not in request.POST:
		return HttpResponseBadRequest("missing rev_kills param!")

	if "prev_round_id" not in request.POST:
		return HttpResponseBadRequest("missing prev_round_id param!")
	
	
	# prevRound = Round.objects.get(request.POST["prev_round_id"])
	prevRound = get_object_or_404(Round, id=request.POST["prev_round_id"])

	newRound = roundManager.create_new_round(
		round_num = prevRound.index + 1,
		start_date = prevRound.end_date.date().isoformat(),
		end_date = (prevRound.end_date.date() + timezone.timedelta(days=7)).isoformat(),

		prog_kills = request.POST["prog_kills"],
		rev_kills = request.POST["rev_kills"],
		direct_pairings = ("direct-pairings" in request.POST)
	)

	template = loader.get_template("assignments/success.html")
	context = {
		'message': 	f"Successfully ended round {prevRound.index}, " +
					f"then successfully created round {newRound.index} with new pairings."
	}
	return HttpResponse(template.render(context, request))



# This is the page that end round directs the user to allow them to select
@login_required(login_url="/accounts/login/")
def createRoundPage(request, prev_round_id):

	# prev_round = get_object_or_404(Round, id=prev_round_id)
	
	template = loader.get_template("assignments/create_round.html")
	context = {
		'prev_round_id': prev_round_id
	}
	return HttpResponse(template.render(context, request))


# MAIN VIEW
@login_required(login_url="/accounts/login/")
def adminControl(request):
	try:
		current_round = getCurRound()

		if current_round is None:
			current_round = getNextRound()
		
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
	
	round_targets = Target.objects.filter(round=current_round).order_by("id")
	round_target_list = list()
	for target in round_targets:
		round_target_list.append(model_to_dict(target))


	all_teams = Team.objects.filter(eliminated=False).order_by("id")
	team_list = list()
	for team in all_teams:
		team_list.append(model_to_dict(team))

	participants = Participant.objects.filter(eliminated_permanently=False).order_by("team_id")
	participant_list = list()
	for participant in participants:
		participant_list.append(model_to_dict(participant))

	template = loader.get_template("assignments/adminControl.html")
	context = {
		'current_round': current_round,
		'current_round_index': current_round_index,
		'eliminated_this_round': len(round_elims),
		'eliminated_permanently': len(perm_elims),
		'remaining': len(remaining),
		'round_targets': round_targets,
		'round_targets_ser': round_target_list,
		'teams': all_teams,
		'team_list': team_list,
		'participants': participant_list,
	}
	return HttpResponse(template.render(context, request))


@login_required(login_url="/accounts/login/")
def eliminateParticipant(request):
	if request.method != 'POST':
		return HttpResponseBadRequest("Must be a POST request!")
	
	"""
	POST PARAMS
	target_id, elimed_participant_id, eliminator_id, date
	"""
	
	if "elimed_participant_id" not in request.POST:
		return HttpResponseBadRequest("missing elimed_participant ID param!")
	if "eliminator_id" not in request.POST:
		return HttpResponseBadRequest("missing eliminator ID param!")
	

	elimed_participant = get_object_or_404(
		Participant, id=int(request.POST["elimed_participant_id"])
	)

	eliminator = get_object_or_404(
		Participant, id=int(request.POST["eliminator_id"])
	)
	
	if "target_id" in request.POST:
		target = get_object_or_404(Target, id=int(request.POST["target_id"]))
	else:
		target = get_object_or_404(Target, target_team=elimed_participant.team, prosecuting_team=eliminator.team)


	if elimed_participant.round_eliminated or elimed_participant.eliminated_permanently:
		# template = loader.get_template("assignments/failedToKill.html")
		template = loader.get_template("assignments/eliminatedParticipant.html")
		context = {
			
		}
		return HttpResponse(template.render(context, request))  

	kill = Kill(
		target = target,
		elimed_participant = elimed_participant,
		eliminator = eliminator,
		date = datetime.datetime.fromisoformat(request.POST["date"])
	)

	kill.save()
	
	elimed_participant.round_eliminated = True
	elimed_participant.save()

	eliminator_name_split = eliminator.name.split(" ")
	eliminator_ln = eliminator_name_split[len(eliminator_name_split) - 1]
	eliminated_name_split = elimed_participant.name.split(" ")
	eliminated_ln = eliminated_name_split[len(eliminated_name_split) - 1]

	drive_text = f"{kill.id}-{eliminator_ln}Killed{eliminated_ln}"

	template = loader.get_template("assignments/eliminatedParticipant.html")
	context = {
		'kill': kill,
		'drive_text': drive_text
	}
	return HttpResponse(template.render(context, request)) 
	# return HttpResponseRedirect(reverse("assignments:admin-control"))


@login_required(login_url="/accounts/login/")
def add_drive_url(request):
	if request.method != 'POST':
		return HttpResponseBadRequest("Must be a POST request!")
	
	"""
	POST PARAMS
	kill_id, video_url
	"""

	print(request.POST)
	
	if "kill_id" not in request.POST:
		return HttpResponseBadRequest("missing kill ID param!")
	if "video_url" not in request.POST:
		return HttpResponseBadRequest("missing video_url  param!")
	

	kill = get_object_or_404(Kill, id = request.POST["kill_id"])
	kill.video_link = request.POST["video_url"]
	kill.save()

	template = loader.get_template("assignments/success.html")
	context = {
		'message': 	f"Successfully added URL!" 
	}
	return HttpResponse(template.render(context, request))


@login_required(login_url="/accounts/login/")
def cleanup_round(request):
	errorTemplate = loader.get_template("assignments/error.html")

	if request.method != 'POST':
		return HttpResponseBadRequest("Must be a POST request!")
	
	# Find the first round that hasn't been marked completed
	round = Round.objects.filter(completed = False).order_by('start_date').first()

	if round is None:
		return HttpResponse(
			errorTemplate.render({'message': "No rounds that haven't already been completed!"}, request)
		)
	
	teams = Team.objects.filter(eliminated = False)

	for team in teams:
		if team.will_progress_in_round():
			team.try_revive()
		else:
			team.eliminate()

	round.completed = True
	round.save()

	"""
	roundManager.create_new_round(
		round_num = round.index + 1,
		start_date = round.end_date.date().isoformat(),
		end_date = (round.end_date.date() + timezone.timedelta(days=7)).isoformat(),
	)
	
	template = loader.get_template("assignments/success.html")
	context = {
		'message': 	f"Successfully ended round {round.index}, " +
					f"then successfully created round {round.index + 1} with new pairings."
	}
	return HttpResponse(template.render(context, request))
	"""
	return HttpResponseRedirect(reverse("assignments:create-round", args=(round.id,)))


def random_date(start_date:datetime.date, end_date:datetime.date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


@login_required(login_url="/accounts/login/")
def create_purge(request):
	if request.method != 'POST':
		return HttpResponseBadRequest("Must be a POST request!")
	
	if "type" not in request.POST:
		return HttpResponseBadRequest("missing 'type' param!")
	if "rules_suspended" not in request.POST:
		return HttpResponseBadRequest("missing 'rules_suspended' param!")
	
	"""
	if "notification_time" not in request.POST:
		return HttpResponseBadRequest("missing 'notification_time' param!")
	
	if "start_time" not in request.POST:
		return HttpResponseBadRequest("missing 'start_time' param!")
	if "end_time" not in request.POST:
		return HttpResponseBadRequest("missing 'end_time' param!")
	"""
	round = getCurRound()
	random_purge_day = random_date(round.start_date.date(), round.end_date.date())
	start = datetime.datetime.combine(
		random_purge_day, 
		datetime.time.fromisoformat(request.POST["start_time"])
	)
	end = datetime.datetime.combine(
		random_purge_day + datetime.timedelta(days=1), 
		datetime.time.fromisoformat(request.POST["end_time"])
	)
	notification = start - datetime.timedelta(hours=12)

	print(f"{start} - {end}")

	
	
	rule_suspension = RuleSuspension(
		type=request.POST["type"],
		rules_suspended=request.POST["rules_suspended"],
		notification_time=notification,
		start_time=start,
		end_time=end,

	)

	rule_suspension.save()
	
	return HttpResponseRedirect(reverse("assignments:admin-control"))
	


@login_required(login_url="/accounts/login/")
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
			
			existingParticipants = Participant.objects.filter(team=existingTeam)
			
			parts = list()
			for part in existingParticipants:
				parts.append(part)

			for name in teammates:
				for i in range(len(parts)):
					if parts[i].name == name:
						parts.pop(i)
						break
				else:
					if len(name) > 0:
						newParticipant = Participant(name=name, team=existingTeam)
						newParticipant.save()
			
			# If there are names that shouldn't exist, remove them
			if len(parts) > 0:
				for part in parts:
					part.delete()

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

"""
def revertThingsFromToday(request):
	recent_changes = Participant.history.as_of(datetime.datetime.today())

	# for change in recent_changes:
	# 	change.history.prev_record()
	# 	change.instance.save()

	return JsonResponse(recent_changes)
"""


def confirmParticipantElimed(kills, participant) -> bool:
	for kill in kills:
		# For each kill see if they would have been revived
		round = kill.target.round

		targets = Target.objects.filter(round=round)

		numKills = 0
		for target in targets:
			numKills += len(target.kills)

		if numKills < round.min_revive_kill_count:
			return True
		
		return False


def confirmGameStatusIsAccurate(request):
	out = {}
	
	participants = Participant.objects.all()

	for participant in participants:
		kills = Kill.objects.query(elimed_participant = participant)

		if len(kills) == 0:
			# print(f"{participant.name} -> F")
			out[participant.id] = {"name": participant.name, "eliminated": "F"}
			continue

		if confirmParticipantElimed(kills, participant):
			# print(f"{participant.name} -> T")
			out[participant.id] = {"name": participant.name, "eliminated": "F"}
		else:
			# print(f"{participant.name} -> F")
			out[participant.id] = {"name": participant.name, "eliminated": "T"}

