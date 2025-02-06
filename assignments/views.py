from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

from assignments.models import Team, Participant, Round, Target



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

		rounds = Round.objects.all()
		

	except (KeyError, Team.DoesNotExist):
		# Redisplay the question voting form.
		return HttpResponseRedirect(reverse("assignments:login"))
	
	else:
		current_round = None
		current_round_index = -1
		for round in rounds: 
			if round.start_date <= timezone.now() and round.end_date > timezone.now():
				current_round = round
				current_round_index = round.index
				break

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
			'target_participants': target_participants,
			'target_name': cur_target.target_team.name,
			'remaining_members': str(remainingMembers)
		}
		return HttpResponse(template.render(context, request))

