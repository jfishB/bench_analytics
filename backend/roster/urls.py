from django.urls import path

from . import views

app_name = "roster"

# When included under /api/v1/roster/, the endpoints below map to:
# - GET/POST /api/v1/roster/players/
# - DELETE /api/v1/roster/players/<id>/
# - GET /api/v1/roster/players/ranked/
urlpatterns = [
    path("players/", views.players, name="players"),
    path("players/<int:player_id>/", views.player_detail, name="player_detail"),
    path("players/ranked/", views.players_ranked, name="players_ranked"),
]
