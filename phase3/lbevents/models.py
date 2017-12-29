from django.db import models


class EventMap(models.Model):
	#id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=256)

	def __str__(self):
		# Subject to change
		return "{}: {}".format(self.id, self.name)

class Event(models.Model):
	#id = models.AutoField(primary_key=True)
	lon = models.DecimalField(max_digits=9, decimal_places=6)
	lat = models.DecimalField(max_digits=9, decimal_places=6)
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
