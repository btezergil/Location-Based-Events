from Event import *
from EventMap import *
import generate

print("**** TESTING EVENT ****\n\n")

# initialization tests (__init__ and getEvent())
evdict = generate.generateone()
print("Inserting event:", evdict, "\n")
ev = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])

print("Event: ", ev, ev.getEvent(), "\n\n")

input("Press enter to continue...\n")
# update tests (updateEvent())
print("Updating event:", ev.getEvent(), "\n")
updatedict = {"title": "this is the updated title", "lat": 85}
print("Update data:", updatedict)
ev.updateEvent(updatedict)
print("Event after update: ", ev.getEvent(), "\n\n\n")

input("Press enter to continue...\n")
# map tests (getMap() and setMap())
print("**** Map tests for the event, setting map of the event: ", ev.getEvent(), "****\n\n\n")

em = EventMap()
print("Event map: ", em, "with id:", em.id)

ev.setMap(em)
print("The map of the event after setMap() operation: ", ev.getMap(), "with id:", ev.getMap().id, "\n\n\n")

input("Press enter to continue...\n")
# inputs with incorrect data
print("**** Testing Event init/update with invalid data: ****\n\n\n")
evdict = generate.generateone()
evdict["lat"] = 255
print("Invalid data(latitude) for init: ", evdict)
try:
    ev2 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
except ValueError as e:
    print("Exception raised: ", e, "\n")

evdict = generate.generateone()
evdict["lon"] = 255
print("Invalid data(longitude) for init: ", evdict)
try:
    ev2 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
except ValueError as e:
    print("Exception raised: ", e, "\n")

evdict = generate.generateone()
evdict["start"] = time.ctime()
print("Invalid data(wrong date format) for init: ", evdict)
try:
    ev2 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
except ValueError as e:
    print("Exception raised: ", e, "\n")

evdict = generate.generateone()
now = time.time()
evdict["start"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now))
evdict["expires"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+3600))
evdict["announce"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+360))
print("Invalid data(announce time after start time) for init: ", evdict)
try:
    ev2 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
except ValueError as e:
    print("Exception raised: ", e, "\n")

evdict = generate.generateone()
now = time.time()
evdict["start"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+7200))
evdict["expires"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now+3600))
evdict["announce"] = time.strftime("%Y/%m/%d %H:%M", time.localtime(now))
print("Invalid data(start time after finish time) for init: ", evdict)
try:
    ev2 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
except ValueError as e:
    print("Exception raised: ", e, "\n\n\n")

input("Press enter to continue...\n")
evdict = generate.generateone()
ev3 = Event(evdict["lon"], evdict["lat"], evdict["location"], evdict["title"], evdict["description"], evdict["category"], evdict["start"], evdict["expires"],evdict["announce"])
print("Event: ", ev3.getEvent())

updatedict = {"lat": 255}
print("Updating with invalid data(latitude): ", updatedict)
try:
    ev3.updateEvent(updatedict)
except ValueError as e:
    print("Exception raised: ", e, "\n")

updatedict = {"lon": 255}
print("Updating with invalid data(longitude): ", updatedict)
try:
    ev3.updateEvent(updatedict)
except ValueError as e:
    print("Exception raised: ", e, "\n")

updatedict = {"from": time.ctime()}
print("Updating with invalid data(wrong date format): ", updatedict)
try:
    ev3.updateEvent(updatedict)
except ValueError as e:
    print("Exception raised: ", e, "\n")

updatedict = {"from": time.strftime("%Y/%m/%d %H:%M", time.localtime(now)), "to": time.strftime("%Y/%m/%d %H:%M", time.localtime(now+3600)), "timetoann": time.strftime("%Y/%m/%d %H:%M", time.localtime(now+360))}
print("Updating with invalid data(announce time after start time): ", updatedict)
try:
    ev3.updateEvent(updatedict)
except ValueError as e:
    print("Exception raised: ", e, "\n")

updatedict = {"from": time.strftime("%Y/%m/%d %H:%M", time.localtime(now+7200)), "to": time.strftime("%Y/%m/%d %H:%M", time.localtime(now+3600)), "timetoann": time.strftime("%Y/%m/%d %H:%M", time.localtime(now))}
print("Updating with invalid data(start time after finish time): ", updatedict)
try:
    ev3.updateEvent(updatedict)
except ValueError as e:
    print("Exception raised: ", e, "\n")

print("Event after invalid update trials: ", ev3.getEvent(), "\n\n")

print("**** EVENT TESTS DONE ****")
