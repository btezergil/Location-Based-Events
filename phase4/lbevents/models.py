from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EventMap(models.Model):
	#id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=256)

	def __str__(self):
		# Subject to change
		return "{}: {}".format(self.id, self.name)

def validate_lat(value):
	if value < -90 or value > 90:
		raise ValidationError(_('%(value)s is not a valid latitude'), params={'value':value},)

def validate_lon(value):
	if value < -180 or value > 180:
		raise ValidationError(_('%(value)s is not a valid longitude'), params={'value':value},)

class Event(models.Model):
	#id = models.AutoField(primary_key=True)
	lon = models.DecimalField(max_digits=9, decimal_places=6, validators=[validate_lon])
	lat = models.DecimalField(max_digits=9, decimal_places=6, validators=[validate_lat])
	locname = models.CharField(max_length=256)
	title = models.CharField(max_length=256)
	desc = models.CharField(max_length=256)
	catlist = models.CharField(max_length=256) # catlist is not a list but a string
	stime = models.DateTimeField()
	to = models.DateTimeField()
	timetoann = models.DateTimeField()
	Map = models.ForeignKey(EventMap, on_delete=models.CASCADE) 

	def __str__(self):
		# Subject to change
		return "{}: {}".format(self.id, self.title)

class Observer(models.Model):
	lon_topleft = models.DecimalField(max_digits=9, decimal_places=6, validators=[validate_lon])
	lat_topleft = models.DecimalField(max_digits=9, decimal_places=6, validators=[validate_lat])
	lon_botright = models.DecimalField(max_digits=9, decimal_places=6, validators=[validate_lon])
	lat_botright = models.DecimalField(max_digits=9, decimal_places=6, validators=[validate_lat])
	category = models.CharField(max_length=256)
	Map = models.ForeignKey(EventMap, on_delete=models.CASCADE)
	session = models.CharField(max_length=256)
