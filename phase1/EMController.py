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
                print("SQL Error while connecting", e)
            
            try:
                cur.execute("select * from MAP where ID='{}'".format(id))
                mapfields = cur.fetchone()
            except Exception as e:
                print("SQL Error during selection of the map", e)
            self.eventmap.id = mapfields[0]
            self.eventmap.name = mapfields[1]
            
            try:
                cur.execute("select e.lon, e.lat, e.locname, e.title, e.desc, e.catlist, e.stime, e.ftime, e.timetoann from EVENT e where parentmap='{}'".format(id))
                mapfields = cur.fetchall()
            except Exception as e:
                print("SQL Error during selection of the events", e)
            
            for e in mapfields:
                newEvent = Event(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8])
                newEvent.setMap(self.eventmap)
            db.close()

    def dettach(self):
        #dettach controller from map and clean all watches
        print("dettach called")

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
            print("SQL Error while connecting", e)
        
        # try to get the map having the name 'name'
        try:
            cur.execute("insert into map (id,name) values ({},'{}')".format(self.eventmap.id,name))
        except Exception as e:
            print("SQL Error during insertion of the map", e)

        try:
            for key,val in self.eventmap.events.items():
                for ev in val:
                    cur.execute('''insert into event (eid, lon, lat, locname, title, desc, catlist, stime, ftime, timetoann, parentmap) 
                        values ({},{},{},'{}','{}','{}','{}','{}','{}','{}',{})'''.format(ev._id, ev.lon, ev.lat, ev.locname, ev.title, ev.desc, " ".join(str(item) for item in ev.catlist), ev.stime, ev.to, ev.timetoann, ev.parentmap.id))
        except Exception as e:
            print("SQL Error during insertion of the events", e)
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
            print("SQL Error while connecting", e)
        
        # try to get the map having the name 'name'
        try:
            cur.execute("select * from MAP where NAME='{}'".format(name))
        except Exception as e:
            print("SQL Error during loading of the map", e)

        # map object is loaded from the database, initialize the EventMap object and return it.
        mapfields = cur.fetchone()
        newmap = EventMap()
        newmap.id, newmap.name = mapfields

        try:
            cur.execute("select e.lon, e.lat, e.locname, e.title, e.desc, e.catlist, e.stime, e.ftime, e.timetoann from EVENT e where parentmap={}".format(newmap.id))
            mapfields = cur.fetchall()
        except Exception as e:
            print("SQL Error during loading of events", e)
        
        for e in mapfields:
            newEvent = Event(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8])
            newEvent.setMap(newmap)
            
        db.close()
        return newmap
    
    @classmethod
    def list(cls):
        ''' Lists all map objects stored in the database '''
        
        maplist = []

        try:
            db = sqlite3.connect("../mapDB.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL Error while connecting", e)
        
        # try to get the map having the name 'name'
        try:
            cur.execute("select name from MAP")
            maps = cur.fetchall()
        except Exception as e:
            print("SQL Error while selecting the maps", e)

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
            print("SQL Error while connecting", e)
        
        # try to get the map having the name 'name'
        try:
            cur.execute("select id from MAP where NAME='{}'".format(name))
            mapid = cur.fetchone()[0]
        except Exception as e:
            print("SQL Error while selecting the map id", e)

        # delete all events of the map, and then delete the map itself
        try:
            cur.execute("delete from EVENT where parentmap={}".format(mapid))
            cur.execute("delete from MAP where id={}".format(mapid))
        except Exception as e:
            print("SQL Error while deleting", e) 
        
        db.commit()
        db.close()