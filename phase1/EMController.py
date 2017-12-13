import sqlite3
from Event import *
from EventMap import *

class EMController:
    def __init__(self, id = 'NEW'):
        self.eventmap = EventMap()
        if id=='NEW':
            self.id = self.eventmap.id
        else:
            try:
                db = sqlite3.connect("../mapDB.db")
                cur = db.cursor()
            except Exception as e:
                print("SQL Error while connecting:", e)
            
            try:
                q = (id,)
                cur.execute("select * from MAP where ID=?", q)
                mapfields = cur.fetchone()
            except Exception as e:
                print("SQL Error during selection of the map:", e)
            self.eventmap.id = mapfields[0]
            self.eventmap.name = mapfields[1]
            
            try:
                cur.execute("select e.lon, e.lat, e.locname, e.title, e.desc, e.catlist, e.stime, e.ftime, e.timetoann, e.eid from EVENT e where parentmap=?", q)
                mapfields = cur.fetchall()
            except Exception as e:
                print("SQL Error during selection of the events:", e)
            
            for e in mapfields:
                newEvent = Event(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8])
                newEvent.setMap(self.eventmap)
                newEvent._id = e[9]
            db.close()

    def dettach(self):
        ''' Dettaches the currently attached EventMap object, cleans all watches and observer list '''
        self.eventmap._observers = [] # TODO:would be better if I did this via a call to EventMap 
        self.eventmap = None

    def __getattr__(self, attr):
        METHOD_LIST = ["insertEvent", "deleteEvent", "searchbyRect", "findClosest", "searchbyTime", "searchbyCategory", "searchbyText", "searchAdvanced", "watchArea"]
        if attr in METHOD_LIST:
            return getattr(self.eventmap, attr)

    def save(self, name):
        ''' Saves currently attached EventMap object into the database '''
        self.eventmap.name = name
        try:
            db = sqlite3.connect("../mapDB.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL Error while connecting:", e)

        # delete all events on the _deleted_events of the eventmap
        try:
            for eventid in self.eventmap._deleted_events:
                q = (eventid,)
                cur.execute("delete from event where eid=?", q)
        except Exception as e:
            print("SQL Error during deletion of the events:", e)

        # try to get the map having the name 'name'
        try:
            q = (self.eventmap.id, name, )
            cur.execute("insert into map (id,name) values (?,?)", q)
        except Exception as e:
            print("SQL Error during insertion of the map:", e)

        try:
            for key,val in self.eventmap.events.items():
                for ev in val:
                    q = (ev._id, ev.lon, ev.lat, ev.locname, ev.title, ev.desc, " ".join(str(item) for item in ev.catlist), ev.stime, ev.to, ev.timetoann, ev.parentmap.id)
                    cur.execute('''insert into event (eid, lon, lat, locname, title, desc, catlist, stime, ftime, timetoann, parentmap) 
                        values (?,?,?,?,?,?,?,?,?,?,?)''', q)
        except Exception as e:
            print("SQL Error during insertion of the events:", e)
        db.commit()
        db.close()
    
    @classmethod
    def load(cls, name):
        ''' Loads the map saved as 'name' in the database and initializes an EventMap object with its attributes
            Returns the EventMap object created
            Is a class method '''
        
        # connect to the database first
        try:
            db = sqlite3.connect("../mapDB.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL Error while connecting:", e)
        
        # try to get the map having the name 'name'
        try:
            q = (name,)
            cur.execute("select * from MAP where NAME=?", q)
        except Exception as e:
            print("SQL Error during loading of the map:", e)

        # map object is loaded from the database, initialize the EventMap object and return it.
        mapfields = cur.fetchone()
        newmap = EventMap()
        newmap.id, newmap.name = mapfields

        try:
            q = (newmap.id,)
            cur.execute("select e.lon, e.lat, e.locname, e.title, e.desc, e.catlist, e.stime, e.ftime, e.timetoann, e.eid from EVENT e where parentmap=?", q)
            mapfields = cur.fetchall()
        except Exception as e:
            print("SQL Error during loading of events:", e)
        
        for e in mapfields:
            newEvent = Event(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8])
            newEvent.setMap(newmap)
            newEvent._id = e[9]
            
        db.close()
        return newmap.id
    
    @classmethod
    def list(cls):
        ''' Lists all map objects stored in the database '''
        
        maplist = []

        try:
            db = sqlite3.connect("../mapDB.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL Error while connecting:", e)
        
        # try to get the map having the name 'name'
        try:
            cur.execute("select name from MAP")
            maps = cur.fetchall()
        except Exception as e:
            print("SQL Error while selecting the maps:", e)

        for m in maps:
            maplist.append(m[0])
        
        db.close()
        return maplist
    
    @classmethod
    def delete(cls, name):
        ''' Deletes the map object stored under name 'name' 
            Is a class method '''

        # connect to the database first
        try:
            db = sqlite3.connect("../mapDB.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL Error while connecting:", e)
        
        # try to get the map having the name 'name'
        try:
            q = (name,)
            cur.execute("select id from MAP where NAME=?", q)
            mapid = cur.fetchone()[0]
        except Exception as e:
            print("SQL Error while selecting the map id:", e)

        # delete all events of the map, and then delete the map itself
        try:
            q = (mapid,)
            cur.execute("delete from EVENT where parentmap=?", q)
            cur.execute("delete from MAP where id=?", q)
        except Exception as e:
            print("SQL Error while deleting:", e) 
        
        db.commit()
        db.close()

    def __getstate__(self):
            return self.__dict__

    def __setstate__(self, d): 
            self.__dict__.update(d)


