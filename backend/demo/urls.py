from django.urls import path

from . import views

urlpatterns = [
	path("", views.demo_list, name="demo-list"),
	path("create/", views.demo_create, name="demo-create"),
	path("<int:item_id>/increment/", views.demo_increment, name="demo-increment"),
]
