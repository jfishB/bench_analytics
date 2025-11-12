from rest_framework import viewsets

from .models import Player, Team
from .serializer import PlayerSerializer, TeamSerializer


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Team model.
    Provides CRUD operations for teams.
    """

    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Player model.
    Provides CRUD operations for players.
    """

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
