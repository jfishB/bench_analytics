"""
- This file handles lineup creation mode determination and orchestrates save/generate operations.
- Imported by:
  - backend/lineups/views.py
"""

from typing import Optional, Tuple
from lineups.models import Lineup
from roster.models import Player as RosterPlayer
from .input_data import CreateLineupInput, LineupPlayerInput
from .databa_access import saving_lineup_to_db
from .validator import validate_lineup_model
from .algorithm_logic import algorithm_create_lineup
from .input_data import CreateLineupInput
from rest_framework.exceptions import ValidationError
from django.utils import timezone


def determine_request_mode(lineup_data: dict) -> Tuple[str, Optional[dict]]:
    """Determine if request is for manual save or algorithm generation.

    Returns:
        - ("manual_save", data) if players list exists with 9 items all having batting_order
        - ("algorithm_generate", None) otherwise (for team_id-only or incomplete players)
    """
    players_data = lineup_data.get("players", [])
    
    # Empty players list or missing players means algorithm generation
    if not players_data:
        return "algorithm_generate", None
    
    # All players must have batting_order for manual save
    all_have_batting_order = all(p.get("batting_order") is not None for p in players_data)

    if all_have_batting_order and len(players_data) == 9:
        return "manual_save", lineup_data
    return "algorithm_generate", None


def handle_lineup_save(validated: dict, user) -> Tuple[Lineup, list]:
    """Persist a lineup from already validated data.

    The view handles all domain validation (batting orders, team/players).
    This function only handles persistence and model validation.

    Args:
        validated: dict from validate_data() containing:
                   - team: Team object
                   - players: list of Player objects
                   - created_by_id: user ID
                   - name: optional lineup name
                   - original_players: list of LineupPlayerInput for batting_order mapping
        user: authenticated user

    Returns:
        (lineup, lineup_players)
    """
    team_obj = validated["team"]
    players_list = validated["players"]
    created_by_id = validated.get("created_by_id")
    lineup_name = validated.get("name") or timezone.now().isoformat()
    original_players = validated.get("original_players", [])

    # Build players payload with batting orders from original input
    players_payload = []
    for player in players_list:
        batting_order = next(
            (p.batting_order for p in original_players if p.player_id == player.id),
            None,
        )
        players_payload.append({"player": player, "batting_order": batting_order})

    lineup, lineup_players = saving_lineup_to_db(team_obj, players_payload, lineup_name, created_by_id)

    # Validate created lineup model
    try:
        result = validate_lineup_model(lineup)
    except Exception as exc:
        raise ValidationError({"detail": str(exc)})
    if result is False:
        raise ValidationError({"detail": "Lineup validation failed."})

    return lineup, lineup_players


def generate_suggested_lineup(team_id: int, player_ids: list | None = None) -> list:
    """Generate a suggested lineup using the algorithm WITHOUT saving to database.

    Args:
        team_id: The team ID to generate lineup for
        player_ids: Optional list of player IDs to constrain the algorithm to

    Returns:
        List of player dictionaries with suggested batting orders
    """

    # Build CreateLineupInput for the algorithm. Limit to 9 players because
    # a lineup only has 9 batting positions; if more than 9 are provided, we take the first 9.
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
