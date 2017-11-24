import sqlite3
from EventMap import *
from Event import *

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
                self.eventmap.insertEvent(newEvent, newEvent.lat, newEvent.lon)
    def dettach(self):
        #dettach controller from map and clean all watches
        print("dettach called")
    def save(self, name):
        ''' Saves currently attached EventMap object into the database '''
        # TODO: set up a database for this and then implement this method
        try:
            db = sqlite3.connect("../mapDB.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL Error while connecting", e)
        
        # try to get the map having the name 'name'
        try:
            cur.execute("select * from MAP where NAME='{}'".format(name))
        except Exception as e:
            print("SQL Error during insertion", e)
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
            print("SQL Error during select", e)

        # map object is loaded from the database, initialize the EventMap object and return it.
        mapfields = cur.fetchone()
        # mapfields is a tuple with all the fields needed to initialize the EventMap object
        
        # before returning CLOSE THE DATABASE CONNECTION with db.close()
        db.close()
    def list(self):
        ''' Lists all map objects stored in the database '''
        print("list called")
    @classmethod
    def delete(cls, name):
        ''' Deletes the map object stored under name 'name' 
            Is a class method '''

        # connect to the database first
        try:
            db = sqlite3.connect("../mapDB.db")
            cur = db.cursor()
        except Exception as e:
            print("SQL Error", e)
        
        # try to get the map having the name 'name'
        try:
            cur.execute("delete from MAP where NAME='{}'".format(name))
        except Exception as e:
            print("SQL Error", e)
        
        # before returning CLOSE THE DATABASE CONNECTION with db.close()
        db.close()
        print("delete class method called")