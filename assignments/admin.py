from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Team, Participant, Round, Target, Kill, RuleSuspension, Issue, Vote

# Cookbook: https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_filter = ["id", "name"]
    search_fields = ["id", "name"]

    fields = ["name", "eliminated", "viewing_code"]
    list_display = ["id", "name", "eliminated", "viewing_code"]

@admin.action(description="Revive Participant")
def revive_participant(modeladmin, request, queryset):
    queryset.update(round_eliminated=False, eliminated_permanently=False)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_filter = ["id", "name", "team", "round_eliminated", "eliminated_permanently"]
    search_fields = ["id", "name"]
    fields = ["name", "team", "round_eliminated", "eliminated_permanently"]
    list_display = ["id", "name", "team", "round_eliminated", "eliminated_permanently"]

    actions = [revive_participant]


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_filter = ["index"]
    search_fields = ["index", "start_date", "end_date"]

@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_filter = ["round", "target_team", "prosecuting_team"]
    search_fields =  ["round", "eliminations"]

@admin.register(Kill)
class KillAdmin(admin.ModelAdmin):
    list_filter = ["target", "elimed_participant", "eliminator"]
    search_fields =  ["date"]

    list_display = ["id", "date", "round", "link_to_target", "elimed_participant_name", "eliminator_name"]

    # fields = ["target", "elimed_participant", "eliminator", "date"]

    def get_target(self, obj):
        return obj.target
    
    def round(self, obj):
        return obj.target.round.index
    
    def target_id(self, obj):
        return obj.target
    
    def link_to_target(self, obj):
        link = reverse("admin:assignments_target_change", args=[obj.target.id])
        return format_html('<a href="{}">Edit {}</a>', link, obj.target.id)
    
    def elimed_participant_name(self, obj):
        return obj.elimed_participant.name
    
    def eliminator_name(self, obj):
        return obj.eliminator.name
    
    # OVERRIDE
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        print(db_field.name)
        if db_field.name == 'elimed_participant':
            if 'instance' in kwargs and kwargs['instance']:
                # kwargs['instance'] is the model
                kwargs['queryset'] = Participant.objects.filter(team=kwargs['instance'].target.target_team)

                print(kwargs['instance'].target.target_team)
                # kwargs['queryset'] = Participant.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def clean(self):
        target = self.target
        elimed_participant = self.elimed_participant
        eliminator = self.eliminator

        if elimed_participant.team != target.target_team:
            raise Exception("Elimed Participant must be on the Target Team!!!")
        
        if eliminator.team != target.prosecuting_team:
            raise Exception("Eliminator Participant must be on the Target Prosecuting Team!!!")


@admin.register(RuleSuspension)
class RuleSuspensionAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields =  []

    list_display = ["id", "type", "notification_time", "start_time", "end_time"]

    # fields = ["target", "elimed_participant", "eliminator", "date"]

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_filter = []
    search_fields =  []

    list_display = ["label", "description", "team_vote", "get_for_votes", "get_against_votes", "did_pass"]

    # fields = ["target", "elimed_participant", "eliminator", "date"]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_filter = ["issue", "team", "in_favor"]
    search_fields =  ["in_favor"]

    list_display = ["issue", "team", "participant", "in_favor"]

    # fields = ["target", "elimed_participant", "eliminator", "date"]


admin.site.site_header = "SA Admin"
admin.site.site_title = "SA Admin Portal"
admin.site.index_title = "Welcome to the Senior Assassin Backend Portal"
        

