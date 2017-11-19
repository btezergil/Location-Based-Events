import sqlite3

class EMController:
    def __init__(self, id = 'NEW'):
        self.id = id
        if self.id=='NEW':
            self.id = EventMap() #should check again when EventMap is implemented
    def dettach(self):
        #dettach controller from map and clean all watches
        print("dettach called")
    def save(self, name):
        ''' Saves currently attached EventMap object into the database '''
        # TODO: set up a database for this and then implement this method
        print("save called")
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
            print("SQL Error", e)
        
        # try to get the map having the name 'name'
        try:
            cur.execute("select * from MAP where NAME='{}'".format(name))
        except Exception as e:
            print("SQL Error", e)

        # map object is loaded from the database, initialize the EventMap object and return it.
        mapfields = cur.fetchone()
        # mapfields is a tuple with all the fields needed to initialize the EventMap object
        
        # before returning CLOSE THE DATABASE CONNECTION with db.close()
        db.close()
        print("load class method called")
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