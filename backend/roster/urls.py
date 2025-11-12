from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "roster"

# DRF Router automatically generates URL patterns
router = DefaultRouter()
router.register(r"teams", views.TeamViewSet, basename="team")
router.register(r"players", views.PlayerViewSet, basename="player")

# Router generates these URLs:
# GET    /teams/          -> list teams
# POST   /teams/          -> create team
# GET    /teams/{id}/     -> retrieve team
# PUT    /teams/{id}/     -> update team
# PATCH  /teams/{id}/     -> partial update team
# DELETE /teams/{id}/     -> delete team
#
# Same pattern for /players/
# Plus custom: GET /players/ranked/

urlpatterns = [
    path("players/", views.players, name="players"),
    path("players/<int:player_id>/", views.player_detail, name="player_detail"),
    path("players/ranked/", views.players_ranked, name="players_ranked"),
]
