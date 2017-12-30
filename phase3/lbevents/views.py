from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import EventMap, Event

def index(request):
	maps = []
	mapmodel = EventMap.objects.all()
	for m in mapmodel:
		maps.append(m)
	try:
		attached_id = request.session['attached_id']
		return render(request, 'maps.html', {'maps':maps, 'attached':True, 'attached_id':attached_id})
	except KeyError: # Not attached to any map yet
		return render(request, 'maps.html', {'maps':maps, 'attached':False})

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

def attach(request, mapid = None):
	try:
		attached_id = request.session['attached_id']
		# Already attached to a map, detach first
		# TODO: All watches will be cleared up
		# Maybe we can put observers as another model
		# and put ForeignKey to its map
		request.session['attached_id'] = mapid
		return redirect(index) # to home page
	except KeyError: # Not attached to any Map
		request.session['attached_id'] = mapid
		return redirect(index) # to home page

def detach(request, mapid = None):
	try:
		attached_id = request.session['attached_id']
		# TODO: All watches will be cleared up
		del request.session['attached_id']
		return redirect(index) # to home page
	except KeyError: # Not attached to any Map
		return redirect(index) # to home page
			
def evinfo(request, mapid = None, eid = None):
	# TODO: Show details of the event
	# TODO: Create a new template to do so
	pass

def createEvent(request, mapid = None):
	m = get_object_or_404(EventMap, pk=mapid)
	try:
		if request.POST['submit'] == 'Add': # form submitted
			_lon = request.POST['lon']
			_lat = request.POST['lat']
			_locname = request.POST['locname']
			_title = request.POST['title']
			_desc = request.POST['desc']
			_catlist = request.POST['catlist']
			_stime = request.POST['stime']
			_to = request.POST['to']
			_timetoann = request.POST['timetoann']
			m.event_set.create(lon=_lon, lat=_lat, locname=_locname, title=_title, desc=_desc, catlist=_catlist, stime=_stime, to=_to, timetoann=_timetoann)
			return redirect(detail, mapid=mapid) # to map
		elif request.POST['submit'] == 'Cancel':
			return redirect(detail, mapid=mapid) # to map
		else:
			return render(request, 'error.html', {'message':'Invalid request'})	
	except KeyError: # Form not submitted yet, show it
		return render(request, 'addevent.html', {'mapid':mapid})
