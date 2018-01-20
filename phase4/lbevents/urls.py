from django.urls import path

from . import views

urlpatterns = [
	path('', views.home, name="Location Based Events"),
	path('list', views.list, name="Location Based Events"),
	path('addmap', views.createmap, name="Create New Map"),
	path('attach/<int:mapid>', views.attach, name="Attach to Map"),
	path('listEvents/<int:mapid>', views.listEvents, name="Events of Map"),
	path('detach/<int:mapid>', views.detach, name="Detach from Map"),
	path('delete/<int:mapid>', views.deletemap, name="Delete Map"),
<<<<<<< HEAD
	path('addevent/<int:mapid>', views.createEvent, name="Create New Event"),
	path('updevent/<int:eid>', views.createEvent, name="Update this Event"),
=======
	path('findclosest/<int:mapid>', views.findclosest, name="Find Closest"),
	path('searchadvanced/<int:mapid>', views.searchadvanced, name="Search Advanced"),
>>>>>>> 611a32f92e244f1385d41c093cb7013b1d256e58
]
