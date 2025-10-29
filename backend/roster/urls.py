from . import views
from django.urls import path, include

app_name = "lineups"

urlpatterns = [
# players endpoint
    path('players/', views.players, name='players'),
    path('players/<int:player_id>/', views.player_detail, name='player_detail'),
    path('players/ranked/', views.players_ranked, name='players_ranked'),
]