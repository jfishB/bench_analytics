import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Player, Team
from .serializer import PlayerSerializer, TeamSerializer
from .services.player_ranking import PlayerRankingService


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

    @action(detail=False, methods=["post"], url_path="sort-by-woba")
    def sort_by_woba(self, request):
        """
        Sort a list of player IDs by wOBA (descending).
        Body: {"player_ids": [1, 2, 3, ...]}
        """
        player_ids = request.data.get("player_ids", [])

        if not player_ids:
            return Response({"error": "player_ids is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sorted_ids = PlayerRankingService.get_ids_sorted_by_woba(player_ids)
            return Response({"player_ids": sorted_ids})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"])
    def ranked(self, request):
        """Get all players ranked by wos_score."""
        from .services.player_ranking import get_ranked_players
        ranked_players = get_ranked_players()
        return Response({"players": ranked_players})

