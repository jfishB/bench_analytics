##########################################
"""
- This file contains service functions for handling
lineup creation requests from the view layer.
- Separates business logic from HTTP handling.
"""
###########################################

from typing import Dict, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from lineups.models import Lineup, LineupPlayer
from roster.models import Player as RosterPlayer

from .input_data import CreateLineupInput, LineupPlayerInput
from .validator import validate_batting_orders, validate_data, validate_lineup_model
from .algorithm_logic import algorithm_create_lineup



def determine_request_mode(request_data: dict) -> Tuple[str, Optional[dict]]:
    """Determine if request is for manual save or algorithm generation.

    Args:
        request_data: The raw request data from the view

    Returns:
        Tuple of (mode, validated_data) where mode is either 'manual_save' or 'algorithm_generate'
    """
    from lineups.serializers import LineupCreate

    req_full = LineupCreate(data=request_data)

    if req_full.is_valid():
        data = req_full.validated_data
        players_data = data["players"]
        all_have_batting_order = all(p.get("batting_order") is not None for p in players_data)

        if all_have_batting_order:
            return "manual_save", data

    return "algorithm_generate", None


def handle_lineup_save(data: dict, user) -> Tuple[Lineup, list]:
    """Handle manual or sabermetrics lineup save with provided batting orders.

    Args:
        data: Validated lineup data with players and batting orders
        user: The authenticated user making the request

    Returns:
        Tuple of (lineup, lineup_players)
    """
    team_id = data["team_id"]
    lineup_name = data.get("name") or f"Lineup - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    players_data = data["players"]

    # Build CreateLineupInput with provided batting orders
    players_input = [
        LineupPlayerInput(
            player_id=p["player_id"],
            batting_order=p.get("batting_order"),
        )
        for p in players_data
    ]

    payload = CreateLineupInput(
        team_id=team_id,
        players=players_input,
        requested_user_id=(user.id if user.is_authenticated else None),
    )

    # Validate batting orders are unique and cover 1-9
    validate_batting_orders(payload.players)
    # Resolve to models (team, players) and created_by id
    validated = validate_data(payload)
    team_obj = validated["team"]
    players_list = validated["players"]
    created_by_id = validated.get("created_by_id")

    # Build payload for saving helper (include player model, position, batting order)
    players_payload = []
    for player in players_list:
        players_payload.append(
            {
                "player": player,
                "batting_order": next((p.batting_order for p in payload.players if p.player_id == player.id), None),
            }
        )

    # Delegate persistence to helper which creates Lineup and LineupPlayer rows
    from .databa_access import saving_lineup_to_db

    lineup, lineup_players = saving_lineup_to_db(team_obj, players_payload, lineup_name, created_by_id)

    # Validate created lineup model
    validate_lineup_model(lineup)

    return lineup, lineup_players


def generate_suggested_lineup(team_id: int, player_ids: list | None = None) -> list:
    """Generate a suggested lineup using the algorithm WITHOUT saving to database.

    Args:
        team_id: The team ID to generate lineup for
        player_ids: Optional list of player IDs to constrain the algorithm to

    Returns:
        List of player dictionaries with suggested batting orders
    """

    # Build CreateLineupInput for the algorithm. Limit to 9 players to avoid
    # factorial explosion; if more than 9 are provided, we take the first 9.
    if player_ids:
        players_inputs = [LineupPlayerInput(player_id=pid) for pid in player_ids][:9]
    else:
        roster_players = list(RosterPlayer.objects.filter(team_id=team_id))
        # If there are no roster players for the team, return empty list
        if not roster_players:
            return []

        # Use up to 9 players from the roster (preserve ordering from DB)
        players_inputs = [LineupPlayerInput(player_id=p.id) for p in roster_players][:9]

    payload = CreateLineupInput(team_id=team_id, players=players_inputs, requested_user_id=None)

    # Call the algorithm which returns a tuple of Player objects in batting order
    lineup_tuple = algorithm_create_lineup(payload)

    if not lineup_tuple:
        # Fallback: return empty suggested list
        return []

    suggested_players = [
        {
            "player_id": p.id,
            "player_name": getattr(p, "name", ""),
            "batting_order": idx + 1,
        }
        for idx, p in enumerate(lineup_tuple)
    ]

    return suggested_players
