import json
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets

from .models import Player, Team
from .serializer import PlayerSerializer, TeamSerializer
from .services.importer import import_from_csv


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
        return JsonResponse({"message": f"Player '{player_name}' deleted successfully"})
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
@require_http_methods(["GET", "POST"])
def load_sample_players(request):
    """API endpoint to load sample players from the CSV file.
    
    GET: Check if players already exist and return status
    POST: Load players from CSV if none exist
    
    Returns:
        - already_loaded: True if players already exist
        - players_count: Number of players in database
        - loaded: Number of players loaded (POST only)
    """
    players_count = Player.objects.count()
    
    if request.method == "GET":
        return JsonResponse({
            "already_loaded": players_count > 0,
            "players_count": players_count,
        })
    
    # POST: Load players from CSV
    if players_count > 0:
        return JsonResponse({
            "already_loaded": True,
            "players_count": players_count,
            "message": "Players are already loaded. Clear existing players first if you want to reload.",
        })
    
    # Find the CSV file - check multiple possible locations
    csv_candidates = [
        Path("data/test_dataset_monte_carlo_bluejays.csv"),  # From repo root (Render)
        Path("../data/test_dataset_monte_carlo_bluejays.csv"),  # From backend/ dir (local)
    ]
    
    csv_path = None
    for candidate in csv_candidates:
        if candidate.exists():
            csv_path = str(candidate)
            break
    
    if not csv_path:
        return JsonResponse({
            "error": "CSV file not found. Looked in: " + ", ".join(str(c) for c in csv_candidates),
        }, status=404)
    
    try:
        result = import_from_csv(csv_path)
        return JsonResponse({
            "success": True,
            "already_loaded": False,
            "players_count": Player.objects.count(),
            "loaded": result.get("created", 0),
            "updated": result.get("updated", 0),
            "messages": result.get("messages", []),
        })
    except Exception as e:
        return JsonResponse({
            "error": f"Failed to load players: {str(e)}",
        }, status=500)
