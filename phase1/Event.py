import EventMap
import re
import time
import sqlite3
import threading

DATEEXP = "^[0-9]{4}/(0[1-9]|1[0-2])/([0-2][0-9]|3[0-1]) ([0-1][0-9]|2[0-3]):([0-5][0-9])$"
datevalidator = re.compile(DATEEXP)

class Event:
    maxidinsession = 0
    def __init__(self, lon, lat, locname, title, desc, catlist, stime, to, timetoann=time.strftime("%Y/%m/%d %H:%M")): 
        try:
    	    db = sqlite3.connect("../mapDB.db")
    	    cur = db.cursor()
        except Exception as e:
            print("SQL Error while connecting")
        try:
            cur.execute("select max(eid) from event")
            evid = cur.fetchone()
            self._id = evid[0]+1+Event.maxidinsession
            Event.maxidinsession += 1
        except Exception as e:
            print("SQL Error during selection of the max map id", e)

        self.evlock = None

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
        self._dataValidator()

    def setLock(self, lock):
        self.evlock = lock
        print(lock)

    def _dataValidator(self, dict = None):
        lat = self.lat
        lon = self.lon
        stime = self.stime
        to = self.to
        timetoann = self.timetoann
        
        if dict != None:
            for k, v in dict.items():
                if k == "lat":
                    lat = v
                elif k == "lon":
                    lon = v
                elif k == "from":
                    stime = v
                elif k == "to":
                    to = v
                elif k == "timetoann":
                    timetoann = v

        stv = datevalidator.match(stime)
        tv = datevalidator.match(to)
        ttav = datevalidator.match(timetoann)
        
        if stv == None or tv == None or ttav == None:
            raise ValueError("Date given in not accepted format or invalid date")
        
        if not -90 < lat < 90:
            raise ValueError("Latitude not in range [-90:90]")
        
        if not -180 < lon < 180:
            raise ValueError("Longitude not in range [-180:180]")
        
        if time.strptime(stime, "%Y/%m/%d %H:%M") > time.strptime(to, "%Y/%m/%d %H:%M"):
            raise ValueError("Start time of the event after finish time")
    
        if time.strptime(timetoann, "%Y/%m/%d %H:%M") > time.strptime(stime, "%Y/%m/%d %H:%M"):
            raise ValueError("Announce time of the event after start time")    
    
    def updateEvent(self, dict):
        ''' Updates the fields of the class from the data in the argument 'dict' '''
        self._dataValidator(dict)
        
        with self.evlock:
            if self.parentmap:
                self.parentmap._deleteFromMap((self.lat, self.lon), self._id)
            
            for key, value in dict.items():
                if key == "from":
                    self.stime = dict["from"]
                    continue
                setattr(self, key, value)
            
            if self.parentmap:
                self.parentmap._insertToMap(self, self.lat, self.lon)
                self.parentmap.eventUpdated(self._id)
        

    def getEvent(self):
        ''' Returns the fields of the class as a dictionary '''
        retdict = self.__dict__.copy()
        retdict.pop("mutex")
        if retdict['parentmap'] != None:
            retdict['parentmap'] = retdict['parentmap'].id # EventMap is not serializable
        return retdict
    
    def setMap(self, mapobj):
        ''' Attaches the event to the map object 'mapobj' '''
        #with self.evlock:
        self.parentmap = mapobj
    
    def getMap(self):
        ''' Returns the map that the event it attached to '''
        return self.parentmap
