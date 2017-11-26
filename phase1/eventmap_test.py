from EMController import *
from Event import *
from EventMap import *
import generate
import kdtree
import random
from threading import Thread

print("**** TESTING EVENTMAP ****\n\n")

def get_input():
	inp = input()
	if inp == 'pass':
		print("Test will be passed\n")
		return 'pass'
	else:
		try:
			n = int(inp)
			return n
		except ValueError as e:
			print("Invalid input given, Test will be passed ", e, "\n")
			return 'pass'

# initialization test (__init__)
print("Testing EventMap.EventMap()","\n")
print("Creating Map:", "\n")
EM = EventMap()

print("Map: ", EM, "\n\n")

# insertEvent tests
print("Testing EventMap.insertEvent(event, lat, lon)\n")
print("Please Enter the number of events to insert:", end=" ")
n=get_input()
if n != 'pass':
	print(n, "Event(s) will be inserted, (lat, lon) will be equal to (event.lat, event.lon)\n")
	for i in range(n):
		evdict = generate.generateone()
		ev = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
		print("Inserting Event:", evdict, "\n")
		EM.insertEvent(ev, ev.lat, ev.lon)
	print("Events in the map and location tree are as follows\n")
	for k, l in EM.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM.tree)
print("Please Enter the number of events to insert:", end=" ")
n = get_input()
if n != 'pass':
	print(n, "Event(s) will be inserted, (lat, lon) will be random (event.lat, event.lon)\n")
	for i in range(n):
		evdict = generate.generateone()
		ev = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
		print("Inserting Event:", evdict, "\n")
		EM.insertEvent(ev, random.uniform(-90,90), random.uniform(-180,180))
	print("Events in the map and location tree are as follows\n")
	for k, l in EM.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM.tree)
print("Please Enter the number of events to insert:", end=" ")
n = get_input()
if n != 'pass':
	print(n, "Event(s) will be inserted, (lat, lon) will be same for all events\n")
	_lat = random.uniform(-90,90)
	_lon = random.uniform(-180,180)
	for i in range(n):
		evdict = generate.generateone()
		ev = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
		print("Inserting Event:", evdict, "\n")
		EM.insertEvent(ev, _lat, _lon)
	print("Events in the map and location tree are as follows\n")
	for k, l in EM.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM.tree)
# deleteEvent tests
print("Testing EventMap.deleteEvent(id)\n")
print("'pass' if would like to pass the test, 1 if would like to continue:", end = " ")
n=get_input()
if n != 'pass':
	length = 1
	for k, l in EM.events.items():
		flag = 0
		for e in l:
			if random.randrange(2) or length == len(EM.events): #coin flip
				_id = e._id
				flag = 1
				break
		length += 1
		if flag:
			break
	print("Deleting a randomly selected event that exists in the map with id =", _id)
	EM.deleteEvent(_id)
	print("Events in the map and location tree are as follows\n")
	for k, l in EM.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM.tree)
	_id = random.uniform(-100000, 100000)
	print("Trying to delete with id =", _id)
	try:
		EM.deleteEvent(_id)
	except Exception as e:
		print("Proper exception raised: ", e)
	print("Events in the map and location tree are as follows\n")
	for k, l in EM.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM.tree)

# eventUpdated tests
print("Testing EventMap.eventUpdated(id)\n")
print("'pass' if would like to pass the test, 1 if would like to continue:", end = " ")
n=get_input()
if n != 'pass':
	evdict = generate.generateone()
	ev = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
	print("Inserting Event:", evdict, "\n")
	ev.setMap(EM)
	print("Events in the map and location tree are as follows\n")
	for k, l in EM.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM.tree)
	print("Updating event:", ev.getEvent(), "\n") 
	updatedict = {"title": "this is the updated title", "lat": 85, "lon": 13}
	ev.updateEvent(updatedict)
	print("Events in the map and location tree are as follows\n")
	for k, l in EM.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM.tree)

# searchbyRect tests
print("Testing EventMap.searchbyRect(lattl, lontl, latbr, lonbr)","\n")
print("Please Enter the number of events:", end = " ")
n=get_input()
if n != 'pass':
	EM2 = EventMap()
	for i in range(n):
		evdict = generate.generateone()
		ev = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
		print("please enter the coordinates to insert, lat =", end=" ")
		x = float(input())
		print("lon =", end=" ")
		y = float(input())
		EM2.insertEvent(ev,x,y)
	print("Events in the map and location tree are as follows\n")
	for k, l in EM2.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM2.tree)
	print("Please specify the rectangle, lattl = ", end=" ")
	_lattl = float(input())
	print("lontl =", end=" ")
	_lontl = float(input())
	print("latbr =", end=" ")
	_latbr = float(input())
	print("lonbr =", end=" " )
	_lonbr = float(input())
	_events = EM2.searchbyRect(_lattl,_lontl,_latbr,_lonbr)
	print("Events in the rectangle are as follows:\n")
	for e in _events:
		print(e.getEvent(),"\n")
#findClosest tests
print("Testing EventMap.findClosest(lat,lon)")
print("Please Enter the number of events:", end = " ")
n=get_input()
if n != 'pass':
	EM2 = EventMap()
	for i in range(n):
		evdict = generate.generateone()
		ev = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
		print("please enter the coordinates to insert, lat =", end=" ")
		x = float(input())
		print("lon =", end=" ")
		y = float(input())
		EM2.insertEvent(ev,x,y)
	print("Events in the map and location tree are as follows\n")
	for k, l in EM2.events.items():
		for e in l:
			print(k, ":", e.getEvent(), "\n")
	kdtree.visualize(EM2.tree)
	print("Please specify the point, lat =", end=" ")
	_lat = float(input())
	print("lon =", end=" ")
	_lon = float(input())
	print(EM2.findClosest(_lat, _lon)[0].getEvent(), "\n")

print("Testing searchbyTime method:")

em = EventMap()
evdict = generate.generateone()
now = time.time()
evdict["start"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+3600))
evdict["expires"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+90000))
evdict["announce"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now))
print("Inserting event:", evdict)
ev1 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev1.setMap(em)

evdict = generate.generateone()
evdict["start"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+90000))
evdict["expires"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+360000))
evdict["announce"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now))
print("Inserting event:", evdict)
ev2 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev2.setMap(em)

evdict = generate.generateone()
evdict["start"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+990000))
evdict["expires"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+996000))
evdict["announce"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now))
print("Inserting event:", evdict)
ev3 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev3.setMap(em)

print("\nFirst time range:", time.strftime("%Y/%m/%d %H:%M", time.localtime(now)), "and", time.strftime("%Y/%m/%d %H:%M", time.localtime(now+100000)), "\n")
reslist = em.searchbyTime(time.strftime("%Y/%m/%d %H:%M", time.localtime(now)), time.strftime("%Y/%m/%d %H:%M", time.localtime(now+100000)))
print("Resulting list is:")
for ev in reslist:
    print(ev.getEvent())

print("\nSecond time range:", time.strftime("%Y/%m/%d %H:%M", time.localtime(now)), "and", time.strftime("%Y/%m/%d %H:%M", time.localtime(now+1000)), "\n")
reslist = em.searchbyTime(time.strftime("%Y/%m/%d %H:%M", time.localtime(now)), time.strftime("%Y/%m/%d %H:%M", time.localtime(now+1000)))
print("Resulting list is:")
for ev in reslist:
    print(ev.getEvent())

print("Testing searchbyCategory method:")

em = EventMap()
evdict = generate.generateone()
evdict["category"] = ["cat1","cat2","cat3"]
print("Inserting event:", evdict)
ev1 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev1.setMap(em)

evdict = generate.generateone()
evdict["category"] = ["cat1","cat2"]
print("Inserting event:", evdict)
ev2 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev2.setMap(em)

evdict = generate.generateone()
evdict["category"] = ["cat2","cat3"]
print("Inserting event:", evdict)
ev3 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev3.setMap(em)

lst = ["cat1","cat2"]
print("\nFirst category list:", lst)
reslist = em.searchbyCategory(lst)
print("Resulting list is:")
for ev in reslist:
    print(ev.getEvent())

lst = ["cat1","cat3"]
print("\nSecond category list:", lst)
reslist = em.searchbyCategory(lst)
print("Resulting list is:")
for ev in reslist:
    print(ev.getEvent())

lst = ["cat3"]
print("\nThird category list:", lst)
reslist = em.searchbyCategory(lst)
print("Resulting list is:")
for ev in reslist:
    print(ev.getEvent())

lst = ["cat4"]
print("\nFourth category list:", lst)
reslist = em.searchbyCategory(lst)
print("Resulting list is:")
for ev in reslist:
    print(ev.getEvent())


#searchbyText tests
print("Testing EventMap.searchbyText(catstr)")
EM = EventMap()
evdict = generate.generateone()
ev = Event(evdict["lon"], evdict["lat"], evdict["location"], "Ceng Party", "This is a very FUN event where StUdEnts get to socialize for once", evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
EM.insertEvent(ev,ev.lat,ev.lon)
evdict = generate.generateone()
ev = Event(evdict["lon"], evdict["lat"], evdict["location"], "Pokemon Party", "PoKeMons gather together to inCreAse their powers", evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
EM.insertEvent(ev,ev.lat,ev.lon)
evdict = generate.generateone()
ev = Event(evdict["lon"], evdict["lat"], evdict["location"], "BusinesS MEEting", "A very SERIOUS meeTING for very SERious Businessmen", evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
EM.insertEvent(ev,ev.lat,ev.lon)
print("Events in the map and location tree are as follows\n")
for k, l in EM.events.items():
	for e in l:
		print(k, ":", e.getEvent(), "\n")
kdtree.visualize(EM.tree)
print("Please Enter the Keyword to search or 'pass' to pass")
keyword = input()
while keyword != 'pass':
	_events = EM.searchbyText(keyword)
	for e in _events:
		print(e.getEvent(),"\n")
	keyword = input()

#searchAdvanced tests
print("Testing EventMap.searchAdvanced(rectangle, from, to, category, text)")
EM = EventMap()
evdict = generate.generateone()
ev = Event(0, 0, evdict["location"], "Search By Text1", "Search By Text1", ["category1"], "1996/01/19 13:13", "2017/10/26 22:12","1995/01/19 13:13")
EM.insertEvent(ev,ev.lat,ev.lon)
evdict = generate.generateone()
ev = Event(10, 10, evdict["location"], "Can't Find Me", "Me neither", ["category2"], "2005/05/12 13:13", "2005/11/13 21:32","1996/01/19 13:13")
EM.insertEvent(ev,ev.lat,ev.lon)
evdict = generate.generateone()
ev = Event(2, 2, evdict["location"], "Search By Text2", "Search By Text2", ["category3"], "2017/01/19 13:13", "2017/10/26 22:12","1996/01/19 13:13")
EM.insertEvent(ev,ev.lat,ev.lon)
print("Events in the map and location tree are as follows\n")
for k, l in EM.events.items():
	for e in l:
		print(k, ":", e.getEvent(), "\n")
kdtree.visualize(EM.tree)
print("Searching with all fields None\n")
res = EM.searchAdvanced(None,None,None,None,None)
for e in res:
	print(e.getEvent(),"\n")
print("Searching with (5,-5,-5,5),'1996/01/19 13:13','2005/06/12 13:13','category1','Search'","\n")
res = EM.searchAdvanced((5,-5,-5,5),'1996/01/19 13:13','2005/06/12 13:13','category1','Search')
for e in res:
	print(e.getEvent(),"\n")

#watchArea Tests
print("Testing EventMap.watchArea(rectangle, callback,category)\n")
_map = EventMap()
obs1 = Thread(target =_map.watchArea, args=((0,0,-1,1),_map,"Music"))
obs2 = Thread(target =_map.watchArea, args=((-1,-1,-3,0),_map,"Music"))
obs3 = Thread(target =_map.watchArea, args=((2,-1,-2,3),_map,"Art"))
print("Creating an observer with args = ((0,0,-1,1),_map,'Music'))")
print("Creating an observer with args = ((-1,-1,-3,0),_map,'Music'))")
print("Creating an observer with args = ((2,-1,-2,3),_map,'Art'))")
obs1.start()
obs2.start()
obs3.start()
ev = Event(0,0,"locname","title","desc","Music","2017/11/03 13:43","2017/11/05 13:43","2017/11/01 13:43")
print("Inserting an event:", ev.getEvent(),"\n")
ev.setMap(_map)
ev.updateEvent({'title':'title is updated'})
_map.deleteEvent(ev.getEvent()['_id'])


