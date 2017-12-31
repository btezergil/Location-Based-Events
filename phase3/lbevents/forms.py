from django.forms import ModelForm
from .models import Event

class AddUpdateEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['lon', 'lat', 'locname', 'title', 'desc', 'catlist', 'stime', 'to', 'timetoann']
