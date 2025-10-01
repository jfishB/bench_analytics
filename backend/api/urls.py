from django.urls import path
from .views import get_message

urlpatterns = [
    path("message/", get_message),
]
