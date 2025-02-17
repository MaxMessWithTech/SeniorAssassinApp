from django.contrib import admin

from .models import Team, Participant, Round, Target, Kill

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_filter = ["id", "name"]
    search_fields = ["id", "name"]

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_filter = ["id", "name", "team"]
    search_fields = ["id", "name"]

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

    # fields = ["target", "elimed_participant", "eliminator", "date"]

    def get_target(self, obj):
        return obj.target
    
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
        
        

