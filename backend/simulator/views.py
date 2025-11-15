"""
API views for the simulator app.
Exposes endpoints for running baseball game simulations.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services.simulation import SimulationService
from .services.player_service import PlayerService
from .serializers import (
    PlayerInputSerializer,
    PlayerNameInputSerializer,
    TeamInputSerializer,
    SimulationResultSerializer,
)


def _run_simulation_and_format_response(batter_stats, num_games):
    """
    Helper function to run simulation and format response.
    Eliminates code duplication across view functions.
    """
    service = SimulationService()
    result = service.simulate_lineup(batter_stats, num_games=num_games)
    
    response_data = {
        "lineup": result.lineup_names,
        "num_games": result.num_games,
        "avg_score": result.avg_score,
        "median_score": result.median_score,
        "std_dev": result.std_dev,
        "min_score": min(result.all_scores),
        "max_score": max(result.all_scores),
        "score_distribution": _calculate_distribution(result.all_scores),
    }
    
    output_serializer = SimulationResultSerializer(response_data)
    return Response(output_serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_by_player_ids(request):
    """
    Simulate games using a lineup specified by player IDs.
    
    POST /api/simulator/simulate-by-ids/
    Body: {
        "player_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "num_games": 1000
    }
    """
    serializer = PlayerInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    player_ids = serializer.validated_data["player_ids"]
    num_games = serializer.validated_data["num_games"]
    
    try:
        player_service = PlayerService()
        batter_stats = player_service.get_players_by_ids(player_ids)
        return _run_simulation_and_format_response(batter_stats, num_games)
        
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Simulation failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_by_player_names(request):
    """
    Simulate games using a lineup specified by player names.
    
    POST /api/simulator/simulate-by-names/
    Body: {
        "player_names": ["Player One", "Player Two", ...],
        "num_games": 1000
    }
    """
    serializer = PlayerNameInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    player_names = serializer.validated_data["player_names"]
    num_games = serializer.validated_data["num_games"]
    
    try:
        player_service = PlayerService()
        batter_stats = player_service.get_players_by_names(player_names)
        return _run_simulation_and_format_response(batter_stats, num_games)
        
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Simulation failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_by_team(request):
    """
    Simulate games using top 9 players from a team (by plate appearances).
    
    POST /api/simulator/simulate-by-team/
    Body: {
        "team_id": 1,
        "num_games": 1000
    }
    """
    serializer = TeamInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    team_id = serializer.validated_data["team_id"]
    num_games = serializer.validated_data["num_games"]
    
    try:
        player_service = PlayerService()
        batter_stats = player_service.get_team_players(team_id, limit=9)
        
        if len(batter_stats) < 9:
            return Response(
                {"error": f"Team {team_id} only has {len(batter_stats)} players, need 9"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return _run_simulation_and_format_response(batter_stats, num_games)
        
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Simulation failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _calculate_distribution(scores):
    """Helper to calculate score distribution."""
    distribution = {}
    for score in scores:
        distribution[score] = distribution.get(score, 0) + 1
    return distribution
