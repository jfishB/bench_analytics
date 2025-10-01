from django.urls import path
from .views import echo_input

urlpatterns = [
    path("echo/", echo_input),
]