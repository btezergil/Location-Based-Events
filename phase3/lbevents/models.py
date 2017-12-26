from django.db import models


class Event(models.Model):
	# TODO: ADD fields of Event
	pass

class EventMap(models.Model):
	#id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=256)
	events = models.ManyToManyField(Event)

