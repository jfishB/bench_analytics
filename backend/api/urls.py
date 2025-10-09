from django.urls import path
from .views import hello, players, delete_player

urlpatterns = [
    path("hello/", hello),
    path("players/", players),
    path("players/<int:player_id>/", delete_player),
]
