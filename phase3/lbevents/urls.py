from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addmap/', views.createMap, name='addmap'),
    path('<int:mapid>/', views.detail, name='detail'),
]
