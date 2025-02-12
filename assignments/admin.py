from django.contrib import admin

from .models import Team, Participant, Round, Target

class TeamAdmin(admin.ModelAdmin):
    list_filter = ["id", "name"]
    search_fields = ["id", "name"]

class ParticipantAdmin(admin.ModelAdmin):
    list_filter = ["id", "name", "team"]
    search_fields = ["id", "name", "team"]

class RoundAdmin(admin.ModelAdmin):
    list_filter = ["index"]
    search_fields = ["index", "start_date", "end_date"]

class TargetAdmin(admin.ModelAdmin):
    list_filter = ["round", "target_team", "prosecuting_team"]
    search_fields =  ["round", "target_team", "prosecuting_team", "eliminations"]

admin.site.register(Team, TeamAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Target, TargetAdmin)
