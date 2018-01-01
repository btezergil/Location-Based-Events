from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Q
from django.contrib import messages

from .models import EventMap, Event
from .forms import AddUpdateEventForm, FindClosestForm, SearchAdvancedForm
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

def deleteMap(request, mapid = None):
	# Check if session is attached to correct map
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		messages.info(request, 'Please attach to the map you wish to delete.')	
		return redirect(index)
	# EndCheck

	m = get_object_or_404(EventMap, pk=mapid)
	with transaction.atomic():
		m.delete()
		#time.sleep(5)
	# OPTIONAL: Add an integrity check here
	messages.error(request, 'Map with id {} deleted.'.format(mapid))
	return redirect(index) 

def detail(request, mapid = None):
	m = get_object_or_404(EventMap, pk=mapid)
	# Need to process and render lat, lon
	# Therefore need to send events from here (mainly px,py)
	events = m.event_set.filter(timetoann__lte=time.strftime("%Y-%m-%d %H:%M"))
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
		messages.info(request, 'Successfully attached to map {}.'.format(m.name))
		return redirect(index) # to home page
	except KeyError: # Not attached to any Map
		m = get_object_or_404(EventMap, pk=mapid) # Check if map exists
		request.session['attached_id'] = mapid
		messages.info(request, 'Successfully attached to map {}.'.format(m.name))
		return redirect(index) # to home page

def detach(request, mapid = None):
	try:
		attached_id = request.session['attached_id']
		# TODO: All watches will be cleared up
		del request.session['attached_id']
		messages.info(request, 'Successfully dettached from map {}.'.format(m.name))
		return redirect(index) # to home page
	except KeyError: # Not attached to any Map
		return redirect(index) # to home page
			
def evinfo(request, mapid = None, eid = None):
	ev = get_object_or_404(Event, pk=eid)
	return render(request, 'eventdetail.html', {'mapid':mapid, 'event':ev})

def _datevalidator(stime, to, timetoann):
	if time.strptime(str(stime)[0:19], "%Y-%m-%d %H:%M:%S") > time.strptime(str(to)[0:19], "%Y-%m-%d %H:%M:%S"):
		raise ValueError("Start time of the event after finish time")
    
	if time.strptime(str(timetoann)[0:19], "%Y-%m-%d %H:%M:%S") > time.strptime(str(stime)[0:19], "%Y-%m-%d %H:%M:%S"):
		raise ValueError("Announce time of the event after start time") 

def evupdate(request, mapid = None, eid = None):

	# Check if session is attached to correct map
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		messages.info(request, 'Please attach to the map the event belongs to.')
		return redirect(detail, mapid=mapid)
	# EndCheck

	#m = get_object_or_404(EventMap, pk=mapid)
	ev = get_object_or_404(Event, pk=eid)
	#m.event_set.get(id=eid).delete()

	try:
		if request.POST['submit'] == 'Update': # form submitted
			form = AddUpdateEventForm(request.POST)
			if form.is_valid():
				ev.lon = form.cleaned_data['lon']
				ev.lat = form.cleaned_data['lat']
				ev.locname = form.cleaned_data['locname']
				ev.title = form.cleaned_data['title']
				ev.desc = form.cleaned_data['desc']
				ev.catlist = form.cleaned_data['catlist']
				ev.stime = form.cleaned_data['stime']
				ev.to = form.cleaned_data['to']
				ev.timetoann = form.cleaned_data['timetoann']
				try:
					_datevalidator(ev.stime, ev.to, ev.timetoann)
				except ValueError as e:
					messages.error(request, "Error, " + str(e))
					return render(request, 'eventupdate.html', {'mapid':mapid, 'form':form, 'eid':eid})
				with transaction.atomic():
					ev.save()
					#m.event_set.update(lon=_lon, lat=_lat, locname=_locname, title=_title, desc=_desc, catlist=_catlist, stime=_stime, to=_to, timetoann=_timetoann)
					#time.sleep(5)
				# OPTIONAL: Add an integrity check here
				messages.info(request, 'Successfully updated event {}.'.format(ev.title))
				return redirect(detail, mapid=mapid) # to map
			else:
				return render(request, 'eventupdate.html', {'mapid':mapid, 'form':form, 'eid':eid})
		elif request.POST['submit'] == 'Cancel':
			return redirect(detail, mapid=mapid) # to map
		else:
			return render(request, 'error.html', {'message':'Invalid request'})	
	except KeyError: # Form not submitted yet, show it
		form = AddUpdateEventForm(instance=ev)
		return render(request, 'eventupdate.html', {'form':form, 'mapid':mapid, 'eid':eid})

def _distance(p1, p2):
	return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def search(request, mapid = None):
	m = get_object_or_404(EventMap, pk=mapid)
	form_fc = FindClosestForm()
	form_sadv = SearchAdvancedForm()
	return render(request, 'search.html', {'mapid':mapid, 'form_fc':form_fc, 'form_sadv':form_sadv})
	
def findClosest(request, mapid = None):
	# TODO: test this method
	# TODO: to details template, add search option
	m = get_object_or_404(EventMap, pk=mapid)
	form = FindClosestForm(request.POST)
	if form.is_valid():
		_lon = form.cleaned_data['lon']
		_lat = form.cleaned_data['lat']
	events = m.event_set.filter(timetoann__lte=time.strftime("%Y-%m-%d %H:%M"))
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
	events = m.event_set.filter(timetoann__lte=time.strftime("%Y-%m-%d %H:%M"))
	form = SearchAdvancedForm(request.POST)
	if form.is_valid():
		stime = form.cleaned_data['stime']
		to = form.cleaned_data['ftime']
		rect = [form.cleaned_data['lat_topleft'], form.cleaned_data['lon_topleft'], form.cleaned_data['lat_botright'], form.cleaned_data['lon_botright']]
		cat = form.cleaned_data['category']
		text = form.cleaned_data['contains']
	else:
		messages.error(request, 'Form not valid, please enter correct values.')
		return redirect(search, mapid=mapid)
	if None not in rect:
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
		messages.info(request, 'Please attach to the map the event belongs to.')
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
		messages.info(request, 'Please attach to the map you wish to add the event to.')
		return redirect(detail, mapid=mapid)
	# EndCheck

	m = get_object_or_404(EventMap, pk=mapid)
	try:
		if request.POST['submit'] == 'Add': # form submitted
			form = AddUpdateEventForm(request.POST)
			if form.is_valid():
				_lon = form.cleaned_data['lon']
				_lat = form.cleaned_data['lat']
				_locname = form.cleaned_data['locname']
				_title = form.cleaned_data['title']
				_desc = form.cleaned_data['desc']
				_catlist = form.cleaned_data['catlist']
				_stime = form.cleaned_data['stime']
				_to = form.cleaned_data['to']
				_timetoann = form.cleaned_data['timetoann']
				try:
					_datevalidator(_stime, _to, _timetoann)
				except ValueError as e:
					messages.error(request, "Error, " + str(e))
					return render(request, 'addevent.html', {'mapid':mapid, 'form':form})
				with transaction.atomic():
					m.event_set.create(lon=_lon, lat=_lat, locname=_locname, title=_title, desc=_desc, catlist=_catlist, stime=_stime, to=_to, timetoann=_timetoann)
					#time.sleep(5)
				# OPTIONAL: Add an integrity check here
					messages.info(request, 'Successfully added event {}.'.format(_title))
					return redirect(detail, mapid=mapid) # to map
			else:
				return render(request, 'addevent.html', {'mapid':mapid, 'form':form})
		elif request.POST['submit'] == 'Cancel':
			return redirect(detail, mapid=mapid) # to map
		else:
			return render(request, 'error.html', {'message':'Invalid request'})	
	except KeyError: # Form not submitted yet, show it
		form = AddUpdateEventForm()
		return render(request, 'addevent.html', {'mapid':mapid, 'form':form})
