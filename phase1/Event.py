import EventMap
import re
import time
import sqlite3

DATEEXP = "^[0-9]{4}/(0[1-9]|1[0-2])/([0-2][0-9]|3[0-1]) ([0-1][0-9]|2[0-3]):([0-5][0-9])$"
datevalidator = re.compile(DATEEXP)

class Event:
    def __init__(self, lon, lat, locname, title, desc, catlist, stime, to, timetoann=time.strftime("%Y/%m/%d %H:%M")):
        try:
    	    db = sqlite3.connect("../mapDB.db")
    	    cur = db.cursor()
        except Exception as e:
            print("SQL Error while connecting")
        try:
            cur.execute("select max(id) from event")
            evid = cur.fetchone()
            self._id = evid[0]+1
        except Exception as e:
            print("SQL Error during selection of the max map id", e)
        
        self.lon = lon 
        self.lat = lat
        self.locname = locname
        self.title = title
        self.desc = desc
        self.catlist = catlist
        self.stime = stime
        self.to = to
        self.timetoann = timetoann
        self.parentmap = None
        #self.announced = True if time.strptime(self.timetoann, "%Y/%m/%d %H:%M") <= time.strftime("%Y/%m/%d %H:%M") else False
        stv = datevalidator.match(stime)
        tv = datevalidator.match(to)
        ttav = datevalidator.match(timetoann)
        if stv == None or tv == None or ttav == None:
            raise ValueError("Date given in not accepted format or invalid date")
        if not -90 < lat < 90:
            raise ValueError("Latitude not in range -90-90")
        if not -180 < lon < 180:
            raise ValueError("Longitude not in range -180-180")
        if time.strptime(self.stime, "%Y/%m/%d %H:%M") > time.strptime(self.to, "%Y/%m/%d %H:%M"):
            raise ValueError("Start time of the event after finish time")
    def updateEvent(self, dict):
        ''' Updates the fields of the class from the data in the argument 'dict' '''
        for key, value in dict.items():
            if key=="from":
                self.stime = dict["from"]
                continue
            setattr(self, key, value)
    def getEvent(self):
        ''' Returns the fields of the class as a dictionary '''
        return self.__dict__
    def setMap(self, mapobj):
        ''' Attaches the event to the map object 'mapobj' '''
        if self.parentmap != None:
            print("event had a parent, performing cleanup from previous map")
            # event belonged to another map before. Delete the event from that map's tree and push it to the new map's tree.
            # TODO: implement deletion method to the tree and then call it from here
        mapobj.insertEvent(self, self.lat, self.lon)
        self.parentmap = mapobj
    def getMap(self):
        ''' Returns the map that the event it attached to '''
        return self.parentmap
