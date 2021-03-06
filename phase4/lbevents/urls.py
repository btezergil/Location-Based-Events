from django.urls import path

from . import views

urlpatterns = [
	path('', views.home, name="Location Based Events"),
	path('list', views.list, name="Location Based Events"),
	path('addmap', views.createmap, name="Create New Map"),
	path('attach/<int:mapid>', views.attach, name="Attach to Map"),
	path('listEvents/<int:mapid>', views.listEvents, name="Events of Map"),
	path('getObs/<int:mapid>', views.getObservers, name="Observers of Map"),
	path('detach/<int:mapid>', views.detach, name="Detach from Map"),
	path('delete/<int:mapid>', views.deletemap, name="Delete Map"),
	path('addevent/<int:mapid>', views.createEvent, name="Create New Event"),
	path('updevent/<int:mapid>/<int:eid>', views.evUpdate, name="Update this Event"),
	path('delevent/<int:mapid>/<int:eid>', views.deleteEvent, name="Delete this Event"),
	path('findclosest/<int:mapid>', views.findclosest, name="Find Closest"),
	path('searchadvanced/<int:mapid>', views.searchadvanced, name="Search Advanced"),
	path('addobs/<int:mapid>', views.addObserver, name="Create An Observer"),
]
