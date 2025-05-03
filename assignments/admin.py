from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Q

from .models import Team, Participant, Round
from .models import Target, Kill, RuleSuspension, Issue, Vote
from .models import ProgressionOverride

from simple_history.admin import SimpleHistoryAdmin

# Cookbook: https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html

@admin.action(description="Revive Team")
def revive_team(modeladmin, request, queryset):
    queryset.update(eliminated=False)


@admin.register(Team)
class TeamAdmin(SimpleHistoryAdmin):
    list_filter = ["id", "name"]
    search_fields = ["id", "name"]

    fields = ["name", "eliminated", "viewing_code"]
    list_display = ["id", "name", "eliminated", "viewing_code"]

    actions = [revive_team]

@admin.action(description="Revive Participant")
def revive_participant(modeladmin, request, queryset):
    queryset.update(round_eliminated=False, eliminated_permanently=False)

@admin.action(description="Permanently Eliminate")
def perm_elim_participant(modeladmin, request, queryset):
    queryset.update(round_eliminated=True, eliminated_permanently=True)

@admin.register(Participant)
class ParticipantAdmin(SimpleHistoryAdmin):
    list_filter = ["id", "name", "team", "round_eliminated", "eliminated_permanently"]
    search_fields = ["id", "name"]
    fields = ["name", "team", "round_eliminated", "eliminated_permanently"]
    list_display = ["id", "name", "team", "round_eliminated", "eliminated_permanently"]
    
    actions = [revive_participant, perm_elim_participant]

@admin.register(Participant.history.model)
class ParticipantHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "team", "round_eliminated", "eliminated_permanently", "history_round_eliminated", "history_eliminated_permanently"]
    
    actions = [revive_participant, perm_elim_participant]


@admin.register(Round)
class RoundAdmin(SimpleHistoryAdmin):
    list_filter = ["index"]
    search_fields = ["index", "start_date", "end_date"]
    list_display = ["index", "start_date", "end_date"]

@admin.register(Target)
class TargetAdmin(SimpleHistoryAdmin):
    list_filter = ["round", "target_team", "prosecuting_team"]
    search_fields =  ["round", "eliminations"]
    list_display = ["round", "eliminations", "target_team", "prosecuting_team"]

@admin.register(Kill)
class KillAdmin(SimpleHistoryAdmin):
    list_filter = ["target__round", "elimed_participant__name", "eliminator__name"]
    search_fields =  ["date", "elimed_participant__name", "eliminator__name"]

    list_display = ["id", "date", "round", "link_to_target", "elimed_participant_name", "eliminator_name", "link"]

    fields = ["elimed_participant", "eliminator", "date", "video_link"]

    def get_target(self, obj):
        return obj.target
    
    def target_id(self, obj):
        return obj.target
    
    def link_to_target(self, obj):
        link = reverse("admin:assignments_target_change", args=[obj.target.id])
        return format_html('<a href="{}">{}</a>', link, obj.target.id)
    
    def link_to_participant(self, obj):
        link = reverse("admin:assignments_participant_change", args=[obj.id])
        return format_html('<a href="{}">{}</a>', link, obj.name)
    
    def link(self, obj):
        if obj.video_link is not None:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.video_link, "Link")
        return "-"
    
    def round(self, obj):
        link = reverse("admin:assignments_round_change", args=[obj.target.round.id])
        return format_html('<a href="{}">{}</a>', link, obj.target.round.index)
    
    # WITH LINK
    def elimed_participant_name(self, obj):
        return self.link_to_participant(obj.elimed_participant)
    
    # WITH LINK
    def eliminator_name(self, obj):
        return self.link_to_participant(obj.eliminator)
    
    # NO LINK
    def get_elimed_name(self, obj):
        print(obj.elimed_participant.name)
        return obj.elimed_participant.name
    get_elimed_name.short_description = 'Eliminated Participant Name'

    
    # NO LINK
    def get_eliminator_name(self, obj):
        return obj.eliminator.name
    

    link_to_target.short_description = "target"
    round.short_description = "round"
    elimed_participant_name.short_description = "eliminated"
    eliminator_name.short_description = "eliminator"
    link.short_description = "Video Link"
    
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
    
    # OVERRIDE
    def clean(self):
        target = self.target
        elimed_participant = self.elimed_participant
        eliminator = self.eliminator

        if elimed_participant.team != target.target_team:
            raise Exception("Elimed Participant must be on the Target Team!!!")
        
        if eliminator.team != target.prosecuting_team:
            raise Exception("Eliminator Participant must be on the Target Prosecuting Team!!!")


@admin.register(RuleSuspension)
class RuleSuspensionAdmin(SimpleHistoryAdmin):
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


@admin.register(ProgressionOverride)
class ProgressionOverrideAdmin(admin.ModelAdmin):
    pass

    # fields = ["target", "elimed_participant", "eliminator", "date"]



admin.site.site_header = "SA Admin"
admin.site.site_title = "SA Admin Portal"
admin.site.index_title = "Welcome to the Senior Assassin Backend Portal"
        

