from dal import autocomplete
from assignments.models import Participant

class ParticipantForm(autocomplete.FutureModelForm):
    class Meta:
        model = Participant
        fields = ('name', 'test')
        widgets = {
            'test': autocomplete.ModelSelect2(
                'select2_one_to_one_autocomplete'
            )
        }