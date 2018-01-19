from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Q
from django.contrib import messages

from .models import EventMap, Event
from .forms import AddUpdateEventForm, FindClosestForm, SearchAdvancedForm, EventMapForm
import time, sys, math, json
from django.http import JsonResponse

def home(request):
	return render(request, "home.html") 

def success(obj, name):
	return JsonResponse({'result':'Success', name:obj})

def error(reason):
	return JsonResponse({'result':'Failed', 'reason':reason})

def getmap(evmap):
	r = {}
	for i in ['id', 'name']:
		r[i] = getattr(evmap, i)
	return r

def list(request):
	maplist = [getmap(m) for m in EventMap.objects.all()]
	try:
		attached_id = request.session['attached_id']
		m = get_object_or_404(EventMap, pk=attached_id)
		return success({'maplist':maplist, 'attachedmap':getmap(m)} , 'success')
	except:
		return success({'maplist':maplist, 'attachedmap':{'id':'None', 'name':'None'}}, 'success')

def createmap(request):
	try:
		f = EventMapForm(request.POST)
		if not f.is_valid():
			raise Exception

		m = EventMap(name=f['name'].value())
		with transaction.atomic():
			m.save()
		return success({'id':m.id, 'message':'Map Created'}, 'success')
	except:
		return error('Invalid form data')

def check_if_attached(session, mapid):
	try:
		is_attached = session['attached_id'] == mapid
		return is_attached
	except KeyError:
		return False

def deletemap(request, mapid=None):
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return error('Cannot delete, try attaching to the Map')

	m = get_object_or_404(EventMap, pk=mapid)
	mid = m.id
	with transaction.atomic():
		m.delete()
	return success({'id':mid, 'message':'Map Deleted'}, 'success')

def attach(request, mapid=None):
	try:
		attached_id = request.session['attached_id']
		# Already attached to a map, detach first
		# TODO: All watches will be cleared up
		# Maybe we can put observers as another model
		# and put ForeignKey to its map
		m = get_object_or_404(EventMap, pk=mapid) # Check if map exists
		request.session['attached_id'] = mapid
		return success({'id':m.id, 'message':'Attached to map'}, 'success')
	except KeyError: # Not attached to any Map
		m = get_object_or_404(EventMap, pk=mapid) # Check if map exists
		request.session['attached_id'] = mapid
		return success({'id':m.id, 'message':'Attached to map'}, 'success')

def getEvent(event):
	# Gets the event in JSON form from the database
	r = {}
	for i in ['lon', 'lat', 'locnane', 'title', 'desc', 'catlist', 'stime', 'to', 'timetoann']:
		r[i] = getattr(event,i)
	return r
	
def evGet(request, eid):
	# Event get request from the browser, get the event via getEvent method and pass its result via success method
	try:
		event = Event.objects.get(id=eid)
		return success(getEvent(event),'event')
	except:
		return error('Event not found')

def evUpdate(request, eid):
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return error('Cannot update, try attaching to the Map')

	ev = get_object_or_404(Event, pk=eid)
	try:
		form = AddUpdateEventForm(request.POST)
		if not form.is_valid():
			raise Exception
		ev.lon = form.cleaned_data['lon']
		ev.lat = form.cleaned_data['lat']
		ev.locname = form.cleaned_data['locname']
		ev.title = form.cleaned_data['title']
		ev.desc = form.cleaned_data['desc']
		ev.catlist = form.cleaned_data['catlist']
		ev.stime = form.cleaned_data['stime']
		ev.to = form.cleaned_data['to']
		ev.timetoann = form.cleaned_data['timetoann']
	except:
		return error('Invalid form')
	try:
		_datevalidator(ev.stime, ev.to, ev.timetoann)
	except ValueError as e:
		return error('Invalid date')

	with transaction.atomic():
		ev.save()
	# CAUTION: Maybe not enough to send a notification message, must send
	# event.id as well so that jquery can reflect the change
	return success('Successfully updated event {}.'.format(ev.title), 'message') 


def deleteEvent(request, mapid = None, eid = None):
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return error('Cannot delete, try attaching to the Map')

	m = get_object_or_404(EventMap, pk=mapid)
	ev = get_object_or_404(m.event_set, pk=eid)
	with transaction.atomic():
		ev.delete()
	# CAUTION: Maybe not enough to send a notification message, must send
	# event.id as well so that jquery can reflect the change
	return success('Deleted the event', 'message') 

def createEvent(request, mapid = None):
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return error('Cannot add event, try attaching to the Map')

	m = get_object_or_404(EventMap, pk=mapid)
	try:
		form = AddUpdateEventForm(request.POST)
		if not form.is_valid():
			raise Exception
		_lon = form.cleaned_data['lon']
		_lat = form.cleaned_data['lat']
		_locname = form.cleaned_data['locname']
		_title = form.cleaned_data['title']
		_desc = form.cleaned_data['desc']
		_catlist = form.cleaned_data['catlist']
		_stime = form.cleaned_data['stime']
		_to = form.cleaned_data['to']
		_timetoann = form.cleaned_data['timetoann']
	except:
		return error('Invalid Form')
	try:
		_datevalidator(_stime, _to, _timetoann)
	except ValueError as e:
		return error('Invalid Date')

	with transaction.atomic():
		m.event_set.create(lon=_lon, lat=_lat, locname=_locname, title=_title, desc=_desc, catlist=_catlist, stime=_stime, to=_to, timetoann=_timetoann)
	return success({'id': ev.id, 'message':'Successfully added event {}.'.format(_title)}, 'success')
