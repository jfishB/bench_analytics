import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets

from .models import Player, Team
from .serializer import TeamSerializer, PlayerSerializer


@csrf_exempt
@require_http_methods(["GET", "POST"])
def players(request):
    """API endpoint to list and create players."""
    if request.method == "GET":
        # List all players with stats
        players = Player.objects.all().values(
            "id",
            "name",
            "xwoba",
            "bb_percent",
            "k_percent",
            "barrel_batted_rate",
            "pa",
            "year",
            "created_at",
            "updated_at",
        )
        player_data = list(players)
        return JsonResponse({"players": player_data})


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


@csrf_exempt
@require_http_methods(["DELETE"])
def player_detail(request, player_id):
    """API endpoint to delete a specific player."""
    try:
        player = Player.objects.get(id=player_id)
        player_name = player.name
        player.delete()
        return JsonResponse({"message": f"Player '{player_name}' deleted successfully"})
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def players_ranked(request):
    """API endpoint to get players ranked by WOS score."""
    try:
        # Fetch all players with stats
        players = Player.objects.all().values(
            "id",
            "name",
            "xwoba",
            "bb_percent",
            "k_percent",
            "barrel_batted_rate",
            "pa",
            "year",
        )
        players_list = list(players)

        """
        Sort by WOS
        sorted_players = sort_players_by_wos(players_list, ascending=False)

        # Add WOS score to each player
        """
        """
        for player in sorted_players:
            player_data = dict(player)
            player_data["wos_score"] = round(calculate_wos(player), 2)
            result.append(player_data)
        """
        result = []

        return JsonResponse({"players": result})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
