from django.urls import path

from . import views

urlpatterns = [
	path('', views.home, name="Location Based Events"),
	path('list', views.list, name="Location Based Events"),
]
