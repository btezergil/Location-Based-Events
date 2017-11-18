class EMController:
    def __init__(self, id = 'NEW'):
        self.id = id
        if self.id=='NEW':
            self.id = EventMap() #should check again when EventMap is implemented
    def dettach(self):
        #dettach controller from map and clean all watches
    def save(self, name):
        #save controlled map and all events in secondary storage
        # TODO: set up a database for this and then implement this method
    def load(cls, name):
        #create a new EventMap object and populate its data from the database
        # CLASS METHOD
    def list(self):
        #list all map objects on database
    def delete(cls, name):
        #delete a map from database
        # CLASS METHOD