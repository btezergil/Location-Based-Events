from Event import *
from EventMap import *
from EMController import *
from socket import *
from threading import Thread
import json
import codecs

helpstr = """Event commands:

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
            EMController watchArea ARGS: Registers an observer with the rectangle and categories given in ARGS
            
            help: Lists all available commands
            exit: Closes the connection to the server WITHOUT SAVING
            """

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
            
            EMController id save MAPNAME: Saves the currently controlled map object under the name MAPNAME into the database
            EMController id dettach: Dettaches the controlled map object and cleans up all watches
            
            EMController commands made to its map:
            
            EMController id insertEvent eventid (lat lon): Inserts the event with eventid into the controlled map, lat,lon are optional and 
                taken from the event by default
            EMController id deleteEvent eventid: Deletes the event with eventid from the controlled map
            EMController id searchbyRect ARGS: Searches for events in the rectangle defined by coordinates in ARGS 
            EMController id findClosest ARGS: Finds the closest event to coordinates given in ARGS 
            EMController id searchbyTime ARGS: Finds all events given in time interval in ARGS
            EMController id searchbyCategory catlist: Finds all events with the categories in catlist
            EMController id searchbyText catlist: Finds all events containing the text in catlist 
            EMController id searchAdvanced ARGS: SearchAdvanced method combining four search methods
            EMController id watchArea ARGS: Registers an observer with the rectangle and categories given in ARGS
            
            help: Lists all available commands
            exit: Closes the connection to the server WITHOUT SAVING
            """

    s = socket(AF_INET, SOCK_STREAM)
    s.connect(('127.0.0.1', port))
    while True:
        inputString = input("Please enter your command: ")
        data = {}

        #parse input string according to rules above, all other commands will be invalid
        inputList = inputString.split(" ")
        if inputList[0] == "exit":
            #close the connection to the socket
            #NOTE:any cleanup necessary? don't think so
            s.close()
            return
        elif inputList[0] == "help":
            print(helpstr)
            input("Press any key to continue")
            continue
        elif inputList[0] == "Event":
            data["ClassName"] = 'Event'
            if inputList[1] == "new":
                #new event is going to be created
                data["Instance"] = None
                data["Method"] = 'new'
                data["Args"] = inputList[2:len(inputList)]
            else:
                try:
                    data["Instance"] = int(inputList[1]) #id of the event
                except ValueError as e:
                    print("Invalid (possibly non-number) id, please check and try again\n")
                    continue
                INSTANCE_METHOD_LIST = ["getEvent", "updateEvent", "getMap"]
                if inputList[2] in INSTANCE_METHOD_LIST:
                    data["Method"] = inputList[2]
                    data["Args"] = inputList[3:len(inputList)]
                else:
                    print("Invalid method called for Event, please check and try again\n")
                    continue
        elif inputList[0] == "EMController":
            data["ClassName"] = 'EMController'
            CLASS_METHOD_LIST = ["new", "list", "load", "delete"]
            INSTANCE_METHOD_LIST = ["save", "dettach", "insertEvent", "deleteEvent", "searchbyRect", "findClosest", "searchbyTime", "searchbyCategory", "searchbyText", "searchAdvanced", "watchArea"]
            if inputList[1] in CLASS_METHOD_LIST:
                data["Instance"] = None
                if inputList[1] == "new":
                    data["Method"] = 'new'
                else:
                    data["Method"] = inputList[1]
                data["Args"] = inputList[2:len(inputList)]
            elif inputList[2] in INSTANCE_METHOD_LIST:
                try:
                    data["Instance"] = int(inputList[1])
                except ValueError as e:
                    print("Invalid (possibly non-number) id, please check and try again\n")
                    continue
                data["Method"] = inputList[2]
                data["Args"] = inputList[3:len(inputList)]
            else:
                print("Invalid method called for EMController, please check and try again\n")
                continue
        else:
            print("Invalid command, please check and try again\n")
            continue
        
        #serialize the data using JSON, send its length and then the data itself
        data = json.dumps(data)
        #print(data, len(data))
        length = len(data)
        s.send(('{:10d}'.format(length)).encode())
        s.send(data.encode())
        

cli = Thread(target=client, args=(20445,))
cli.start()
