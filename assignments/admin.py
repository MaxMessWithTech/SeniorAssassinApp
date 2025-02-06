from django.contrib import admin

from .models import Team, Participant, Round, Target

admin.site.register(Team)
admin.site.register(Participant)
admin.site.register(Round)
admin.site.register(Target)
