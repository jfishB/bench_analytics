"""
- This file handles lineup persistence logic.
- Imported by:
    - backend/lineups/interactor.py
"""
from typing import Optional, Tuple
from lineups.models import Lineup
from .databa_access import saving_lineup_to_db
from .validator import validate_lineup_model
from .exceptions import DomainError
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


def handle_lineup_save(val_data: dict, original_batting_orders: list) -> Tuple[Lineup, list]:
    """Persist a lineup from already validated data.

    The view handles all domain validation (batting orders, team/players).
    This function only handles persistence and model validation.

    Args:
        validated: dict from validate_data() containing:
                   - team: Team object
                   - players: list of Player objects
                   - created_by_id: user ID
                   - name: optional lineup name

    Returns:
        (lineup, lineup_players)
    """
    team_obj = val_data["team"]
    players_list = val_data["players"]
    created_by_id = val_data.get("created_by_id")
    lineup_name = val_data.get("name") or timezone.now().isoformat()

    # Build players payload with batting orders (1-indexed position in validated list)
    players_payload = []
    for player in players_list:
        players_payload.append(
            {
                "player": player,
                "batting_order": original_batting_orders[players_list.index(player)],
            }
        )

    lineup, lineup_players = saving_lineup_to_db(team_obj, players_payload, lineup_name, created_by_id)

    # Validate created lineup model
    try:
        result = validate_lineup_model(lineup)
    except Exception as exc:
        raise DomainError(str(exc))
    if result is False:
        raise DomainError("Lineup validation failed.")

    return lineup, lineup_players
