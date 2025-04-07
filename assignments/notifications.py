from assignments.models import Kill, Issue
from django.utils import timezone

class Notifications:
	def __init__(self):
		self.notifications = list()
	
	def add(self, header:str, body:str, link:str, link_text:str):
		self.notifications.append({ "header": header, "body": body, "link": link, "link_text": link_text })

	def addKill(self, kill:Kill):
		self.add(
			"New Kill",
			f"{kill.eliminator.name} killed {kill.elimed_participant.name} on {kill.date.strftime('%B %d')}",
			kill.video_link,
			"none"
		)

	def addKills(self, kills:list[Kill]):
		for kill in kills:
			timedelta = kill.date - timezone.now().date()
			if timedelta.days <= 7: 
				self.addKill(kill=kill)
				   

	def addIssue(self, issue: Issue, team_code:str):
		self.add(
			"New Vote",
			f"{issue.label}. For: {issue.get_for_votes()}, against: {issue.get_against_votes()}, required to pass: {issue.get_majority()}",
			f"/vote/{team_code}/{issue.id}",
			"Vote"
		)

	def addIssues(self, issues: list[Issue], team_code:str):
		for issue in issues:
			self.addIssue(issue=issue, team_code=team_code)

	def addStatus(self):
		self.add(
			"VIEW ROUND STATUS",
			"If you would like to see videos and information about everyone in the round, click this button",
			"/status",
			"View"
		)

	def get(self):
		return self.notifications