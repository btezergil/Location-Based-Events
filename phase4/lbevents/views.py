from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Q
from django.contrib import messages

from .models import EventMap, Event
from .forms import AddUpdateEventForm, FindClosestForm, SearchAdvancedForm, EventMapForm, ObserverForm
import time, sys, math, json
from subprocess import Popen, PIPE
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
	print(request.session.session_key)
	try:
		attached_id = request.session['attached_id']
		m = get_object_or_404(EventMap, pk=attached_id)
		return success({'maplist':maplist, 'session_key':request.session.session_key, 'attachedmap':getmap(m)} , 'success')
	except:
		return success({'maplist':maplist, 'session_key':request.session.session_key, 'attachedmap':{'id':'None', 'name':'None'}}, 'success')

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
		m = get_object_or_404(EventMap, pk=mapid) # Check if map exists
		m.observer_set.filter(session__exact=request.session.session_key).delete()	
		request.session['attached_id'] = mapid
		return success({'id':m.id, 'message':'Attached to map'}, 'success')
	except KeyError: # Not attached to any Map
		m = get_object_or_404(EventMap, pk=mapid) # Check if map exists
		request.session['attached_id'] = mapid
		return success({'id':m.id, 'message':'Attached to map'}, 'success')

def listEvents(request, mapid):
	m = EventMap.objects.get(id=mapid)
	try:
		evlist = []
		for ev in m.event_set.all():
			dic = ev.__dict__.copy()
			dic['lat'] = float(ev.lat)
			dic['lon'] = float(ev.lon)
			dic['stime'] = ev.stime.strftime("%Y-%m-%d %H:%M")
			dic['to'] = ev.to.strftime("%Y-%m-%d %H:%M")
			dic['timetoann'] = ev.timetoann.strftime("%Y-%m-%d %H:%M")
			del dic['_state']
			evlist.append(dic)
		return success({'evlist':evlist, 'session_key':request.session.session_key}, 'success')
	except Exception as e:
		print(repr(e))
		return error('Cannot list events of the map')

def getObservers(request, mapid):
	m = EventMap.objects.get(id=mapid)
	try:
		obslist = []
		for obs in m.observer_set.all():
			if (request.session.session_key != obs.session):
				continue;
			dic = obs.__dict__.copy()
			dic['lat_topleft'] = float(obs.lat_topleft)
			dic['lon_topleft'] = float(obs.lon_topleft)
			dic['lat_botright'] = float(obs.lat_botright)
			dic['lon_botright'] = float(obs.lon_botright)
			del dic['_state']
			obslist.append(dic)
			print(dic)
		print(obslist)
		return success({'obslist':obslist}, 'success')
	except Exception as e:
		print(repr(e))
		return error('Cannot list events of the map')

def detach(request, mapid=None):
	try:
		attached_id = request.session['attached_id']
		m = get_object_or_404(EventMap, pk=mapid) # Check if map exists
		m.observer_set.filter(session__exact=request.session.session_key).delete()
		del request.session['attached_id']
		return success('Detached from Map', 'message')
	except KeyError: # Not attached to any Map
		return error('Must be attached to the Map before detach')

def findclosest(request, mapid=None):
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
	return success({'id':closest[0].id, 'message':'Find Closest result'}, 'success')

def searchadvanced(request, mapid = None):
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
		return error('Invalid Form')
	
	if None not in rect:
		try:
			_rectvalidator(rect[1], rect[0], rect[3], rect[2])
		except ValueError as e:
			return error('Invalid Rect, ' + e.str())
		events = events.filter(lat__lte=rect[0], lat__gte=rect[2], lon__gte=rect[1], lon__lte=rect[3])
	if stime != None and to !=None:
		events = events.filter(to__gte=stime, stime__lte=to)
	if cat != None:
		events = events.filter(catlist__icontains=cat)
	if text != None:
		events = events.filter(Q(title__icontains=text) | Q(desc__icontains=text))
	r = [e.id for e in events]
	return success({'ids':r, 'message':'Search Advanced result'}, 'success')

def _distance(p1, p2):
	return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def getEvent(event):
	# Gets the event in JSON form from the database
	r = {}
	for i in ["id", "locname", "title", "desc", "catlist"]:
		r[i] = getattr(event,i)
	for i in ["lon", "lat"]:
		r[i] = str(float(getattr(event,i)))
	for i in ["stime", "to", "timetoann"]:
		r[i] = getattr(event,i).strftime("%Y-%m-%d %H:%M")
	return r
	
def evGet(request, eid):
	# Event get request from the browser, get the event via getEvent method and pass its result via success method
	try:
		event = Event.objects.get(id=eid)
		return success(getEvent(event),'event')
	except:
		return error('Event not found')

def _sendtosocket(ev, tag):
	jsoninfo = getEvent(ev)
	jsoninfo["eid"] = jsoninfo["id"]
	jsoninfo["id"] = "*"
	jsoninfo["message"] = "Event " + tag
	jsoninfo["tag"] = tag
	cmd = "printf \'{}\'".format(json.dumps(jsoninfo))
	print(cmd)
	cmdnc = "nc -u -w 1 127.0.0.1 9999"
	p = Popen(cmd, shell=True, stdout=PIPE)
	q = Popen(cmdnc, shell=True, stdin=p.stdout)

def evUpdate(request, mapid, eid):
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return error('Cannot update, try attaching to the Map')

	ev = get_object_or_404(Event, pk=eid)
	try:
		form = AddUpdateEventForm(request.POST)
		if not form.is_valid():
			raise Exception
		ev.lon = form['lon'].value()
		ev.lat = form['lat'].value()
		ev.locname = form['locname'].value()
		ev.title = form['title'].value()
		ev.desc = form['desc'].value()
		ev.catlist = form['catlist'].value()
		ev.stime = form['stime'].value()
		ev.to = form['to'].value()
		ev.timetoann = form['timetoann'].value()
	except:
		return error('Invalid form')
	try:
		_datevalidator(ev.stime, ev.to, ev.timetoann)
	except ValueError as e:
		return error('Invalid date,' + str(e))

	with transaction.atomic():
		ev.save()

	ev = get_object_or_404(Event, pk=eid)
	_sendtosocket(ev, "MODIFY")

	return success('Successfully updated event {}.'.format(ev.title), 'message') 

def deleteEvent(request, mapid = None, eid = None):
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return error('Cannot delete, try attaching to the Map')

	m = get_object_or_404(EventMap, pk=mapid)
	ev = get_object_or_404(m.event_set, pk=eid)

	_sendtosocket(ev, "DELETE")

	with transaction.atomic():
		ev.delete()
	
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
        _lon = form['lon'].value()
        _lat = form['lat'].value()
        _locname = form['locname'].value()
        _title = form['title'].value()
        _desc = form['desc'].value()
        _catlist = form['catlist'].value()
        _stime = form['stime'].value()
        _to = form['to'].value()
        _timetoann = form['timetoann'].value()
    except:
    	return error('Invalid Form')
    try:
    	_datevalidator(_stime, _to, _timetoann)
    except ValueError as e:
        return error('Invalid Date')

    with transaction.atomic():
        m.event_set.create(lon=_lon, lat=_lat, locname=_locname, title=_title, desc=_desc, catlist=_catlist, stime=_stime, to=_to, timetoann=_timetoann)
    
    ev = m.event_set.get(lon=_lon, lat=_lat, locname=_locname, title=_title, desc=_desc, catlist=_catlist, stime=_stime, to=_to, timetoann=_timetoann)

    _sendtosocket(ev, "INSERT")	

    return success({'id': ev.id, 'message':'Successfully added event {}.'.format(_title)}, 'success')

def _datevalidator(stime, to, timetoann):
	if time.strptime(str(stime)[0:16], "%Y-%m-%d %H:%M") > time.strptime(str(to)[0:16], "%Y-%m-%d %H:%M"):
		raise ValueError("Start time of the event after finish time")
    
	if time.strptime(str(timetoann)[0:16], "%Y-%m-%d %H:%M") > time.strptime(str(stime)[0:16], "%Y-%m-%d %H:%M"):
		raise ValueError("Announce time of the event after start time") 

def addObserver(request, mapid = None):
	is_attached = check_if_attached(request.session, mapid)
	if not is_attached:
		return error('Cannot add observer, try attaching to the Map')

	m = get_object_or_404(EventMap, pk=mapid)
	try:
		form = ObserverForm(request.POST)
		if not form.is_valid():
			raise Exception
		_lontl = form['lon_topleft'].value()
		_lattl = form['lat_topleft'].value()
		_lonbr = form['lon_botright'].value()
		_latbr = form['lat_botright'].value()
		_category = form.cleaned_data['category']
	except:
		return error('Invalid Form')
	try:
		_rectvalidator(_lontl, _lattl, _lonbr, _latbr)
	except ValueError as e:
		return error('Invalid Rect, ' + e.str())

	with transaction.atomic():
		m.observer_set.create(lon_topleft = _lontl, lat_topleft = _lattl, lon_botright = _lonbr, lat_botright = _latbr, category = _category, session = request.session.session_key)
	obs = m.observer_set.get(lon_topleft = _lontl, lat_topleft = _lattl, lon_botright = _lonbr, lat_botright = _latbr, category = _category)
	return success({'id':obs.id, 'message':'Successfully added observer'}, 'success')

def _rectvalidator(lontl, lattl, lonbr, latbr):
	if lattl <= latbr:
		raise ValueError("Top left latitude must be greater than bottom right latitude")
    
	if lonbr <= lontl:
		raise ValueError("Bottom right longitude must be greater than top left longitude") 
