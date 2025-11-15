"""
URL configuration for simulator app.
"""

from django.urls import path

from simulator import views

app_name = "simulator"

urlpatterns = [
    path("simulate-by-ids/", views.simulate_by_player_ids, name="simulate-by-ids"),
    path("simulate-by-names/", views.simulate_by_player_names, name="simulate-by-names"),
    path("simulate-by-team/", views.simulate_by_team, name="simulate-by-team"),
]
