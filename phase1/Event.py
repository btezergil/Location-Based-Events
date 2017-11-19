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
        self.parent_map = None;
    def updateEvent(self, dict):
        for key, value in dict.items():
            setattr(self, key, value)
    def getEvent(self):
        return self.__dict__
    def setMap(self,mapobj):
        # will be implemented when map is completed
        self.parent_map = mapobj
    def getMap(self):
        return self.parent_map
