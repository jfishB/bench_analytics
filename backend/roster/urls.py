from django.urls import include, path
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

urlpatterns = [
    path("", include(router.urls)),
    path("sort-by-woba/", views.sort_players_by_woba, name="sort-by-woba"),
    # Public: check if sample players are loaded
    path("sample-players-status/", views.check_sample_players_status,
         name="sample-players-status"),
    # Admin only: load sample players from CSV
    path("load-sample-players/", views.load_sample_players,
         name="load-sample-players"),
]
