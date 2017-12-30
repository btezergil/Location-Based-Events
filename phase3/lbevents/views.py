from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Q

from .models import EventMap, Event
import time, sys, math

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
	# Concurrency seems working, uncomment sleep for test
	try:
		if request.POST['submit'] == 'Add': # form submitted
			map_name = request.POST['name']
			with transaction.atomic():
				em = EventMap(name=map_name)
				em.save()
				#time.sleep(5)
			# OPTIONAL: Add an integrity check here
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
		px = ev.lon
		py = ev.lat
		eid = ev.id
		title = ev.title
		# 800px => px = 1000 - ( (lon + 180)/360 )*1000
		px = ( (px + 180)/360 )*800
		# 400py => py = ( (lat + 90)/180 )*500
		py = 400 - ( (py + 90)/180 )*400
		ev_infos[eid] = {'px':px, 'py':py, 'title':title}
	try:
		if request.session['attached_id'] == m.id:
			is_attached = True
		else:
			is_attached = False
		return render(request, 'detail.html', {'map':m, 'ev_infos':ev_infos, 'is_attached':is_attached})
	except KeyError:
		return render(request, 'detail.html', {'map':m, 'ev_infos':ev_infos, 'is_attached':False})

def attach(request, mapid = None):
	try:
		attached_id = request.session['attached_id']
		# Already attached to a map, detach first
		# TODO: All watches will be cleared up
		# Maybe we can put observers as another model
		# and put ForeignKey to its map
		m = get_object_or_404(EventMap, pk=mapid) # Check if map exists
		request.session['attached_id'] = mapid
		return redirect(index) # to home page
	except KeyError: # Not attached to any Map
		m = get_object_or_404(EventMap, pk=mapid) # Check if map exists
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
	# TODO: put deleteEvent href to the template
	pass

def _distance(p1, p2):
	return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
	
def findClosest(request, mapid = None):
	# TODO: test this method
	# TODO: to details template, add search option
	m = get_object_or_404(EventMap, pk=mapid)
	_lon = request.POST['lon']
	_lat = request.POST['lat']
	events = m.event_set.all()
	min_dist = sys.maxsize
	closest = []
	for e in events:
		cur_dist = _distance((_lat, _lon), (e.lat, e.lon))
		if cur_dist <= min_dist:
			min_dist = cur_dist
			closest = [e]
	return render(request, 'queryResult.html', {'events':closest})

def searchAdvanced(request, mapid = None):
	# TODO: test this method
	# TODO: to details template, add search option
	m = get_object_or_404(EventMap, pk=mapid)
	events = m.event_set.all()
	try:
		rect = request.session['rectangle']
		# Note that rectangle is an array[4]
	except KeyError:
		rect = None
	try:
		stime = request.session['stime']
		to = request.session['to']
	except KeyError:
		stime = None
		to = None
	try:
		cat = request.session['category']
	except KeyError:
		cat = None
	try:
		text = request.session['text']
	except KeyError:
		text = None
	if rect != None:
		events = events.filter(lat__lte=rect[0], lat__gte=rect[2], lon__gte=rect[1], lon__lte=rect[3])
	if stime != None and to !=None:
		events = events.filter(to__gte=stime, stime__lte=to)
	if cat != None:
		events = events.filter(catlist__icontains=cat)
	if text != None:
		events = events.filter(Q(title__icontains=text) | Q(desc__icontains=text))
	return render(request, 'queryResult.html', {'events':events})
		
def deleteEvent(request, mapid = None, eid = None):
	# TODO: test this method after evinfo is implemented
	# Concurrency seems working, uncomment sleep for test
	
	# Check if session is attached to correct map
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return redirect(evinfo, mapid=mapid, eid=eid)
	# EndCheck

	m = get_object_or_404(EventMap, pk=mapid)
	ev = get_object_or_404(m.event_set, pk=eid)
	with transaction.atomic():
		ev.delete()
		#time.sleep(5)
	# OPTIONAL: Add an integrity check here
	return redirect(detail, mapid) 

def check_if_attached(session, mapid):
	try:
		is_attached = session['attached_id'] == mapid
		return is_attached
	except KeyError:
		return False

def createEvent(request, mapid = None):
	# Concurrency seems working, uncomment sleep for test

	# Check if session is attached to correct map
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return redirect(detail, mapid=mapid)
	# EndCheck

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
			with transaction.atomic():
				m.event_set.create(lon=_lon, lat=_lat, locname=_locname, title=_title, desc=_desc, catlist=_catlist, stime=_stime, to=_to, timetoann=_timetoann)
				#time.sleep(5)
			# OPTIONAL: Add an integrity check here
			return redirect(detail, mapid=mapid) # to map
		elif request.POST['submit'] == 'Cancel':
			return redirect(detail, mapid=mapid) # to map
		else:
			return render(request, 'error.html', {'message':'Invalid request'})	
	except KeyError: # Form not submitted yet, show it
		return render(request, 'addevent.html', {'mapid':mapid})
