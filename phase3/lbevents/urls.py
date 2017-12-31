from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addmap/', views.createMap, name='addmap'),
    path('attach/<int:mapid>', views.attach, name='attach'),
    path('detach/<int:mapid>', views.detach, name='detach'),
    path('detail/<int:mapid>/', views.detail, name='detail'),
    path('detail/<int:mapid>/<int:eid>', views.evinfo, name='evinfo'),
    path('detail/<int:mapid>/<int:eid>/update', views.evupdate, name='evupdate'),
    path('detail/<int:mapid>/addevent', views.createEvent, name='addevent'),
    path('detail/<int:mapid>/<int:eid>/deleteEvent', views.deleteEvent, name='deleteEvent'),
    path('queryResult/findClosest/<int:mapid>', views.findClosest, name='findClosest'),
    path('queryResult/<int:mapid>', views.searchAdvanced, name='search'),
]
