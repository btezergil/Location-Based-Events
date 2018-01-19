from django.urls import path

from . import views

urlpatterns = [
	path('', views.home, name="Location Based Events"),
	path('list', views.list, name="Location Based Events"),
	path('addmap', views.createmap, name="Create New Map"),
	path('attach/<int:mapid>', views.attach, name="Attach to Map"),
]
