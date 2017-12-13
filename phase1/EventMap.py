import kdtree
import re
import sqlite3
from Event import *
import time

TIMEEXP = "^(?P<date>([0-9]{4}/(0[1-9]|1[0-2])/([0-2][0-9]|3[0-1]) ([0-1][0-9]|2[0-3]):([0-5][0-9])))|\+((?P<number>[0-9]*) ((?P<hours>hours)|(?P<days>days)|(?P<minutes>minutes)|(?P<months>months)))$"
timevalidator = re.compile(TIMEEXP)

class EventMap:
	maxidinsession = 0
	def __init__(self):
		self.events = {}
		self.tree = kdtree.create(dimensions = 2)
		self.name = "default"
		self._observers = []
		self._deleted_events = []
		try:
			db = sqlite3.connect("../mapDB.db")
			cur = db.cursor()
		except Exception as e:
			print("SQL Error while connecting", e)
		try:
			cur.execute("select max(id) from map")
			mapid = cur.fetchone()
			self.id = mapid[0]+1+EventMap.maxidinsession
			EventMap.maxidinsession += 1
		except Exception as e:
			print("SQL Error during selection of the max map id", e)
		db.close()

	def _insertToMap(self, event, lat, lon, notifyFlag = False):
		event_point = (event.lat, event.lon)
		point = (lat,lon)
		if point == (None,None):
               		point = event_point
		if event_point != point:
			new_info = {}
			for key in ['lon','lat','locname','title','desc','catlist','stime','to','timetoann']:
				if key == 'lon':
					new_info[key] = lon
				elif key == 'lat':
					new_info[key] = lat
				else:
					new_info[key] = getattr(event, key)
			event.updateEvent(new_info)
		if point not in self.events:
			self.events[point] = [event]
			self.tree.add(point)
		else:
			self.events[point].append(event)
		if not self.tree.is_balanced:
			self.tree = self.tree.rebalance()
		if notifyFlag:
			self.notify("INSERT", event)
	
	def insertEvent(self, event, lat, lon):
		self._insertToMap(event, lat, lon, True)
		event.setMap(self)

	def _deleteEventFromkdtree(self, point):
		self.tree = self.tree.remove(point)
		if not self.tree.is_balanced:
			self.tree = self.tree.rebalance()

	def _checkforid(self, eid): #Checks if given id exists in the map
		for k,l in self.events.items():
			for e in l:
				if eid == e._id:
					return true
		return false

	def deleteEvent(self, eid):
		try:
			_event = self._findEventFromMap(eid)
			if _event == None:
				raise ValueError("Event with given id does not lie in the map")
			_point = _event.lat, _event.lon
			self._deleteFromMap(_point, eid, True)
			self._deleted_events.append(eid)
		except ValueError as valerr:
			print(valerr)

	def _deleteFromMap(self, _point, eid, notifyFlag = False):
		if self.events[_point] == None:
			raise ID_ERROR('Given event ID does not exist in the EventMap')
		elif len(self.events[_point]) == 1: # Point only contains one event
			if notifyFlag:
				self.notify("DELETE", self.events[_point][0])
			del self.events[_point]
			self._deleteEventFromkdtree(_point)
		else:
			for event in self.events[_point]:
				if eid == event._id:
					if notifyFlag:
						self.notify("DELETE", event)
					self.events.remove(event)
					break

	def _findEventFromMap(self, eid):
		for point, lst in self.events.items():
			for event in lst:
				if eid == event._id:
					return event
	
	def eventUpdated(self, eid):
		try:
			_updated = self._findEventFromMap(eid)
			if _updated == None:
				raise ValueError("Event with given id does not lie in the map")
			self._deleted_events.append(eid)
			self.notify("MODIFY", _updated)
		except ValueError as valerr:
			print(valerr)

	def searchbyRect(self, lattl, lontl, latbr, lonbr):
		mid_point = ((lattl + latbr)/2, (lontl + lonbr)/2)
		radius = sum([(x - y)**2 for x,y in zip(mid_point, (lattl,lontl))])
		in_radius = self.tree.search_nn_dist(mid_point, radius + 1) # +1 is for overcoming the within constraint (optional)
		result = []
		for point in in_radius:
			if (latbr <= point[0] <= lattl) and (lontl <= point[1] <= lonbr):
				result.append(point)
		events = []
		for point in result:
			events = events + self.events[point]
		return events 
			

	def findClosest(self, lat, lon):
		point = (lat, lon)
		return self.events[self.tree.search_nn(point)[0].data]
	
	@staticmethod
	def _datestr_to_sec(datestr):
		'''Taking String of the date as the argument, returns the seconds passed for the date.
			datestr matches to one of the forms from the validator'''
		datestrv = timevalidator.match(datestr)
		if datestrv == None:
			raise ValueError("Date given in not accepted format or invalid date")
		if datestrv.group('date'): #Input format as in YYYY/MM/DD HH:MM
			return time.mktime(time.strptime(datestr,"%Y/%m/%d %H:%M"))
		elif datestrv.group('number'): #Input format as in +num (hours|days|minutes|months)
			number = int(datestrv.group('number'))
			if datestrv.group('hours'): # +X hours
				return time.time() + number * 3600 #X Hours(3600*X seconds) from now
			elif datestrv.group('days'): # +X days
				return time.time() + number * 604800 #X Days(24*7*3600*X seconds) from now
			elif datestrv.group('minutes'): # +X minutes
				return time.time() + number * 60 #X Minutes(60*X seconds) from now
			elif datestrv.group('months'): # +X months
				return time.time() + number * 18144000 	#X Months(30*days seconds) from now
									#This is potentially buggy(not %100 accurate),
									#Each month is taken as 30 days				
	@staticmethod
	def _overlap(s1, e1, s2, e2):
		'''Computes if there is an overlap in the ranges (s1, e1) and (s2, e2)'''
		return e1 >= s2 and e2 >= s1	#might be hard to understand why
						#refer to https://nedbatchelder.com/blog/201310/range_overlap_in_two_compares.html

	def searchbyTime(self, stime, to): 
		result = []
		stv = timevalidator.match(stime)
		tv = timevalidator.match(to)
		if stv == None or tv == None:
			raise ValueError("Date given in not accepted format or invalid date")
		stime_in_sec = self. _datestr_to_sec(stime)
		to_in_sec = self._datestr_to_sec(to)
		for k,l in self.events.items():
			for event in l:
				ev_stime_in_sec = self._datestr_to_sec(event.stime)
				ev_to_in_sec = self._datestr_to_sec(event.to)
				if self._overlap(stime_in_sec, to_in_sec, ev_stime_in_sec, ev_to_in_sec):
					result.append(event)
		return result
					
	def searchbyCategory(self, catstr): 
		result = []		
		for k,l in self.events.items():
			for event in l:
				for cat in event.catlist:
					if cat in catstr:
						if event not in result:
							result.append(event)
		return result
	
	def searchbyText(self, catstr): 
		result = []
		for k,l in self.events.items():
			for event in l:
				if catstr.lower() in event.title.lower() or catstr.lower() in event.desc.lower(): #catstr is in either one
					result.append(event)
		return result

	def searchAdvanced(self,rectangle, stime, to, category, text): 
		res_rect = None
		res_time = None
		res_cat = None
		res_text = None
		if rectangle != None:
			res_rect = self.searchbyRect(rectangle[0],rectangle[1],rectangle[2],rectangle[3]) #Only if rectangle is a 4-tuple
		if stime != None and to != None:
			res_time = self.searchbyTime(stime, to)
		if category != None:
			res_cat = self.searchbyCategory(category)
		if text != None:
			res_text = self.searchbyText(text)
		if (None,None,None,None) == (res_rect,res_time,res_cat,res_text): #Return all events(No Constraint)
			result = []
			for k,l in self.events.items():
				for event in l:
					result.append(event)
			return result
		else:
			s = set()
			for i in (res_rect,res_time,res_cat,res_text):
				if i != None:
					if s == set():
						s = set(i)
						break

			for i in (res_rect,res_time,res_cat,res_text):
				s = s.intersection(set(i))
			
			return list(s)		
	
	def register(self,obs):
		self._observers.append(obs)

	def unregister(self,obs):
		try:
			self._observers.remove(obs)
		except:
			print("not an observer")
			pass

	@staticmethod
	def in_view_area(rectangle, point):
		return  rectangle[2] <= point[0] <= rectangle[0] and rectangle[1] <= point[1] <= rectangle[3] 
			# rectangle.latbr <= point.lat <= rectangle.lattl and
			# rectangle.lontl <= point.lon <= rectangle.lonbr

	def notify(self, call_type, event):
		for o in self._observers:
			if o.category:
				if o.category in event.catlist and self.in_view_area(o.rectangle, (event.lat, event.lon)):
					o.update(self, call_type, event)
			else:
				if self.in_view_area(o.rectangle, (event.lat, event.lon)):
					o.update(self, call_type, event)

	def watchArea(self, rectangle, callback, category = None):
		newObs = MapObs(rectangle, self, category)

	def __getstate__(self): 
		return self.__dict__

	def __setstate__(self, d): 
		self.__dict__.update(d)
			

class MapObs:
	def __init__(self, rectangle, subj, category = None):
		self.rectangle = rectangle
		self.category = category
		subj.register(self)
	
	def update(self, subj, call_type, event):
		if call_type == "INSERT":
			print("Event inserted: {}".format(event.getEvent()))
		elif call_type == "MODIFY":	
			print("Event modified: {}".format(event.getEvent()))
		elif call_type == "DELETE":
			print("Event deleted: {}".format(event.getEvent()))
