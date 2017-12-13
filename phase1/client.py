from Event import *
from EventMap import *
from EMController import *

def client(port):
    """ Client gives text input from terminal. Input gets formatted into a JSON object and sent to its worker through the socket. 
        Input format is "CLASSNAME INSTANCE METHOD ARGS" where classname is either Event or EMController, method is one of their respective
        methods, and args are the arguments of that respective method. Instance is the object that this method will be called on.
        Instances will be determined by the id of the object, which is unique.
        
        The client will not keep any instance of any object, can only reach them through calls to the worker.  Available commands:
            
            Event commands:

            Event new ARGS: Creates a new Event object with arguments ARGS
            Event id getEvent: Gets the event with id id
            Event id updateEvent ARGS: Updates the Event object with the given args
            Event id getMap: Gets the map the Event object with id id is attached to
            
            EMController commands:
            
            EMController new: Creates a new EMController object with a new map
            EMController list: Lists all available maps in database with their names
            EMController load MAPNAME: Loads the map with name MAPNAME into a new EMController object and returns it
            EMController delete MAPNAME: Delets the map with name MAPNAME from the database
            EMController save MAPNAME: Saves the currently controlled map object under the name MAPNAME into the database
            EMController dettach: Dettaches the controlled map object and cleans up all watches
            
            EMController commands made to its map:
            
            EMController insertEvent eventid (lat lon): Inserts the event with eventid into the controlled map, lat,lon are optional and 
                taken from the event by default
            EMController deleteEvent eventid: Deletes the event with eventid from the controlled map
            EMController searchbyRect ARGS: Searches for events in the rectangle defined by coordinates in ARGS 
            EMController findClosest ARGS: Finds the closest event to coordinates given in ARGS 
            EMController searchbyTime ARGS: Finds all events given in time interval in ARGS
            EMController searchbyCategory catlist: Finds all events with the categories in catlist
            EMController searchbyText catlist: Finds all events containing the text in catlist 
            EMController searchAdvanced ARGS: SearchAdvanced method combining four search methods
            EMController watchArea ARGS: Registers an observer with the rectangle and categories given in ARGS"""