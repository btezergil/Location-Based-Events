import EventMap

class Event:
    def __init__(self, lon, lat, locname, title, desc, catlist, stime, to, timetoann):
        self.lon = lon
        self.lat = lat
        self.locname = locname
        self.title = title
        self.desc = desc
        self.catlist = catlist
        self.stime = stime
        self.to = to
        self.timetoann = timetoann
        self.parent_map = None
    def updateEvent(self, dict):
        ''' Updates the fields of the class from the data in the argument 'dict' '''
        for key, value in dict.items():
            setattr(self, key, value)
    def getEvent(self):
        ''' Returns the fields of the class as a dictionary '''
        return self.__dict__
    def setMap(self, mapobj):
        ''' Attaches the event to the map object 'mapobj' '''
        if self.parent_map != None:
            print("event had a parent, performing cleanup from previous map")
            # event belonged to another map before. Delete the event from that map's tree and push it to the new map's tree.
            # TODO: implement deletion method to the tree and then call it from here
        mapobj.insertEvent(self, self.lat, self.lon)
        self.parent_map = mapobj
    def getMap(self):
        ''' Returns the map that the event it attached to '''
        return self.parent_map
