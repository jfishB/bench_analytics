import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from .models import Player, Team
from .serializer import PlayerSerializer, TeamSerializer
from .services.sample_data_loader import load_sample_players as load_sample_data


# TODO: implement post as well for clarity
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


# TODO: what does this do is it needed clarify?
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
        return JsonResponse(
            {"message": f"Player '{player_name}' deleted successfully"}
        )
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# TODO: get rid of old method
@csrf_exempt
@require_http_methods(["GET"])
def players_ranked(request):
    """API endpoint to get players ranked by WOS score."""
    try:
        # TODO: Implement actual WOS ranking logic
        # For now, returns empty list as placeholder
        result = []

        return JsonResponse({"players": result})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def sort_players_by_woba(request):
    """API endpoint to sort a list of player IDs by wOBA (descending).

    Request body should be JSON: {"player_ids": [1, 2, 3, ...]}
    Returns: {"player_ids": [sorted_ids...]} with highest wOBA first
    """
    try:
        data = json.loads(request.body)
        player_ids = data.get("player_ids", [])

        if not player_ids:
            return JsonResponse({"error": "player_ids is required"}, status=400)

        # Fetch players with the given IDs and sort by xwoba descending
        players = Player.objects.filter(id__in=player_ids).order_by("-xwoba")

        # Return the sorted player IDs
        sorted_ids = [player.id for player in players]

        return JsonResponse({"player_ids": sorted_ids})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def check_sample_players_status(request):
    """Check if sample players are loaded (public endpoint).

    Returns:
        - already_loaded: True if players already exist
        - players_count: Number of players in database
        - team_id: The team ID that players belong to
    """
    players_count = Player.objects.count()
    default_team, _ = Team.objects.get_or_create(pk=1)

    return JsonResponse(
        {
            "already_loaded": players_count > 0,
            "players_count": players_count,
            "team_id": default_team.id,
        }
    )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def load_sample_players(request):
    """Load sample players from CSV (admin only).

    This endpoint requires admin authentication.
    Regular users should not be able to load data into the database.

    Returns:
        - success: bool
        - already_loaded: bool
        - players_count: Number of players in database
        - team_id: The team ID that players belong to
        - loaded/updated counts
    """
    result = load_sample_data(team_id=1)

    if not result.get("success"):
        return JsonResponse(result, status=500)

    return JsonResponse(result)
