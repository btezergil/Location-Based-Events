from django import forms
from django.forms import ModelForm
from .models import EventMap, Event

class EventMapForm(ModelForm):
    class Meta:
        model = EventMap
        fields = ['name']

class AddUpdateEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['lon', 'lat', 'locname', 'title', 'desc', 'catlist', 'stime', 'to', 'timetoann']
        

class FindClosestForm(ModelForm):
    class Meta:
        model = Event
        fields = ['lon', 'lat']

class SearchAdvancedForm(forms.Form):
    stime = forms.DateTimeField(label = "Time from", required = False)
    ftime = forms.DateTimeField(label = "Time to", required = False)
    contains = forms.CharField(label = "String to be searched", required = False)
    category = forms.CharField(label = "Categories", required = False)
    lat_topleft = forms.DecimalField(label = "Top left latitude", required = False)
    lon_topleft = forms.DecimalField(label = "Top left longitude", required = False)
    lat_botright = forms.DecimalField(label = "Bottom right latitude", required = False)
    lon_botright = forms.DecimalField(label = "Bottom right longitude", required = False)

class ObserverForm(forms.Form):
    category = forms.CharField(label = "Categories", required = False)
    lat_topleft = forms.DecimalField(label = "Top left latitude")
    lon_topleft = forms.DecimalField(label = "Top left longitude")
    lat_botright = forms.DecimalField(label = "Bottom right latitude")
    lon_botright = forms.DecimalField(label = "Bottom right longitude")