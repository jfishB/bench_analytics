from . import views
from .views import LineupCreateView
from django.urls import path, include

app_name = "lineups"

urlpatterns = [
# lineups endpoint
    path("lineups/", LineupCreateView.as_view(), name="lineup-create"), 
]