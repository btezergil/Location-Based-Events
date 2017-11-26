from EMController import *
from Event import *
from EventMap import *
import sqlite3
import generate

print("**** TESTING EMCONTROLLER ****\n\n")

try:
    db = sqlite3.connect("../mapDB.db")
    cur = db.cursor()
except Exception as e:
    print("SQL Error", e)


# initialization tests, list() method test

print("Initializing empty EMController")
ec1 = EMController()

print("Empty EMController:", ec1, "with new EventMap with id:", ec1.eventmap.id, "its events:", ec1.eventmap.events)
input("Press enter to continue...\n")

print("Checking database for existing EventMaps via EMController.list()")
print("Query result:", EMController.list(),"\n")

print("Initializing EMController with map 'deneme'")
ec2 = EMController(0)
print("EMController:", ec2, "with new EventMap with id:", ec2.eventmap.id, "and name:", ec2.eventmap.name)
try:
    q = (ec2.eventmap.id,)
    cur.execute("select * from map where id=?", q)
    res = cur.fetchone()
except Exception as e:
    print("SQL Error", e)

print("Whereas in the database, EventMap id:", res[0], "and name:", res[1], "\n")

print("Number of events in EventMap:", len(list(ec2.eventmap.events.values())[0]), "and events:", list(ec2.eventmap.events.values())[0][0].getEvent())
try:
    q = (res[0],)
    cur.execute("select * from event where parentmap=?", q)
    res = cur.fetchall()
except Exception as e:
    print("SQL Error", e)

print("Number of events fetched from database:", len(res), "and events:", res)
input("Press enter to continue...\n")

print("Loading same database via EMController.load() method:\n")
ec3 = EMController(EMController.load("deneme"))
print("Loaded map:", ec3.eventmap.id, "and name:", ec3.eventmap.name)
print("Number of events in EventMap:", len(list(ec3.eventmap.events.values())[0]), "and events:", list(ec3.eventmap.events.values())[0][0].getEvent())
input("Press enter to continue...\n")

print("Inserting new events to blank created EventMap and saving it under the name 'test'")
evdict = generate.generateone()
print("Inserting event:", evdict)
ev1 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev1.setMap(ec1.eventmap)

evdict = generate.generateone()
print("Inserting event:", evdict)
ev2 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev2.setMap(ec1.eventmap)

evdict = generate.generateone()
print("Inserting event:", evdict)
ev3 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
ev3.setMap(ec1.eventmap)

print("\nCurrent status of EventMap with id:", ec1.eventmap.id, "and its events:", ec1.eventmap.events, "\n")
print("Number of events:", len(list(ec1.eventmap.events.values())), "and events:")
for evntlst in list(ec1.eventmap.events.values()):
    for evnt in evntlst:
        print(evnt.getEvent())
input("\nPress enter to continue...\n\n")


ec1.save("test")
print("Event saved in the database, checking integrity:")

try:
    q = (ec2.eventmap.id,)
    cur.execute("select * from map where id=?", q)
    res = cur.fetchone()
except Exception as e:
    print("SQL Error", e)

print("In the database, EventMap id:", res[0], "and name:", res[1], "\n")

try:
    q = (res[0],)
    cur.execute("select * from event where parentmap=?", q)
    res = cur.fetchall()
except Exception as e:
    print("SQL Error", e)

print("Number of events fetched from database:", len(res), "and events:", res)

input("\nPress enter to continue...\n\n")

print("Deleting the EventMap created in the database under the name 'test'\n")

EMController.delete('test')

print("Querying database after deletion for the map named 'test':")

try:
    q = ('test',)
    cur.execute("select * from map where name=?", q)
    res = cur.fetchone()
except Exception as e:
    print("SQL Error", e)

print("Query result is:",res)

print("Dettaching the map from:", ec3, ", its map:", ec3.eventmap)
dettachedmap = ec3.eventmap
ec3.dettach()
print("Map after dettach:", ec3.eventmap)
print("List of watches in the previously watched map object(should be cleared by dettach):", dettachedmap._observers)


print("**** EMCONTROLLER TESTS DONE ****")
