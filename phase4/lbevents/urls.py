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
	path('addevent/<int:mapid>', views.createEvent, name="Create New Event"),
	path('updevent/<int:eid>', views.createEvent, name="Update this Event"),
]
