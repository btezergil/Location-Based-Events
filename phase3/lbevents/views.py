from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import EventMap, Event

def index(request):
	maps = []
	mapmodel = EventMap.objects.all()
	for m in mapmodel:
		maps.append(m)
	return render(request, 'maps.html', {'maps':maps})

def createMap(request):
	try:
		if request.POST['submit'] == 'Add': # form submitted
			map_name = request.POST['name']
			em = EventMap(name=map_name)
			em.save()
			return redirect(index) # to home page
		elif request.POST['submit'] == 'Cancel':
			return redirect(index) # to home page
		else:
			return render(request, 'error.html', {'message':'Invalid request'})
	except KeyError: # Form not submitted yet, show it
		return render(request, 'addmap.html')

def detail(request, mapid = None):
	m = get_object_or_404(EventMap, pk=mapid)
	# Need to process and render lat, lon
	# Therefore need to send events from here (mainly px,py)
	events = m.event_set.all()
	ev_infos = {}
	for ev in events:
		px = ev.lat
		py = ev.lon
		eid = ev.id
		title = ev.title
		# 600px => px = 600 - ( (lat + 90)/180 )*600
		px = 600 - ( (px + 90)/180 )*600
		# 600py => py = ( (lon + 180)/360 )*600
		py = ( (py + 180)/360 )*600
		ev_infos[eid] = {'px':px, 'py':py, 'title':title}
	return render(request, 'detail.html', {'map':m, 'ev_infos':ev_infos})
	
