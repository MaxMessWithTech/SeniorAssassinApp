from django import forms
from dal import autocomplete
from assignments.models import Participant, Target, Kill

 
class EliminateParticipantForm(forms.Form):
    target = forms.ModelChoiceField(
        queryset=Target.objects.all(),
        widget=autocomplete.ModelSelect2(url='targetAutocomplete')
    )
    elimed_participant = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        widget=autocomplete.ModelSelect2(url='participantAutocomplete')
    )
    eliminator = forms.ModelChoiceField(
        queryset=Participant.objects.all(),
        widget=autocomplete.ModelSelect2(url='participantAutocomplete')
    )
    target_id = forms.DateField()


    
    