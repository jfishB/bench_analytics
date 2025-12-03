"""
rest api endpoints for running baseball simulations.
three endpoints: simulate by player ids, player names, or team id.
uses player_service.py to fetch data from database,
simulation.py to run monte carlo simulations,
and serializers.py to validate input/output.
requires authentication via isAuthenticated permission.

monte carlo simulation engine based on bram stoker's baseball-simulator:
https://github.com/BramStoker/baseball-simulator
"""

import logging
from collections import Counter

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    PlayerInputSerializer,
    PlayerNameInputSerializer,
    SimulationResultSerializer,
    TeamInputSerializer,
)
from .services.player_service import PlayerService
from .services.simulation import SimulationService

logger = logging.getLogger(__name__)


def _handle_simulation_request(player_input, num_games, fetch_method):
    """
    Helper to handle simulation request with consistent error handling.

    Args:
        player_input: Player IDs, names, or team ID
        num_games: Number of games to simulate
        fetch_method: 'ids', 'names', or 'team'

    Returns:
        Response object with simulation results or error
    """
    try:
        player_service = PlayerService()

        # Fetch players based on method
        if fetch_method == "ids":
            batter_stats = player_service.get_players_by_ids(player_input)
        elif fetch_method == "names":
            batter_stats = player_service.get_players_by_names(player_input)
        elif fetch_method == "team":
            batter_stats = player_service.get_team_players(
                player_input, limit=9)
            if len(batter_stats) < 9:
                return Response(
                    {
                        "error": (
                            f"Team {player_input} only has "
                            f"{len(batter_stats)} players. Need 9."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response({"error": "Invalid fetch method"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return _run_simulation_and_format_response(batter_stats, num_games)

    except ValueError as e:
        # Player not found or data validation error
        logger.warning(f"ValueError in simulation: {str(e)}")
        return Response(
            {"error": str(
                e), "hint": "Check that all player IDs/names exist and have valid statistics."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        # Unexpected error - log for debugging
        logger.error(f"Simulation failed: {str(e)}", exc_info=True)
        return Response(
            {"error": "An unexpected error occurred during simulation.",
                "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _run_simulation_and_format_response(batter_stats, num_games):
    """
    Helper function to run simulation and format response.
    Eliminates code duplication across view functions.
    """
    service = SimulationService()
    result = service.simulate_lineup(batter_stats, num_games=num_games)

    # Handle empty scores edge case
    if not result.all_scores:
        return Response(
            {"error": "Simulation produced no results. Check input data."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
    Requires exactly 9 player IDs (standard baseball lineup).

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

    return _handle_simulation_request(player_ids, num_games, fetch_method="ids")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_by_player_names(request):
    """
    Simulate games using a lineup specified by player names.
    Requires exactly 9 player names (standard baseball lineup).

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

    return _handle_simulation_request(player_names, num_games, fetch_method="names")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_by_team(request):
    """
    Simulate games using top 9 players from a team (by plate appearances).
    Automatically selects exactly 9 players with most plate appearances.

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

    return _handle_simulation_request(team_id, num_games, fetch_method="team")


def _calculate_distribution(scores):
    """
    Helper to calculate score distribution efficiently using Counter.
    Counter is optimized for counting occurrences in large datasets.
    """
    return dict(Counter(scores))
