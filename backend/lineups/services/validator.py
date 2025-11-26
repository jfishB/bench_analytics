"""
- This file defines validation logic for lineup data and models.
- Imported by:
  - backend/lineups/views.py
  - backend/lineups/services/lineup_creation_handler.py
  - backend/lineups/services/algorithm_logic.py
  - backend/lineups/interactor.py
"""
from django.contrib.auth import get_user_model
from .databa_access import fetch_players_by_ids, fetch_team_by_id
from .exceptions import BadBattingOrder, NoCreator, PlayersNotFound, PlayersWrongTeam, TeamNotFound


def validate_batting_orders(players):
    """Validate that batting orders are unique and cover positions 1-9.

    Args:
        players: List of LineupPlayerInput objects or similar objects with batting_order attribute

    Raises:
        BadBattingOrder: If batting orders are invalid (missing, not unique, or don't cover 1-9)
    """
    # Extract batting orders
    batting_orders = []
    for p in players:
        # Support both dataclass attributes and dict keys
        if hasattr(p, "batting_order"):
            bo = p.batting_order
        elif isinstance(p, dict):
            bo = p.get("batting_order")
        else:
            bo = None

        if bo is None:
            raise BadBattingOrder("All players must have a batting order assigned")
        batting_orders.append(bo)

    # Check that we have exactly 9 players
    if len(batting_orders) != 9:
        raise BadBattingOrder(f"Lineup must have exactly 9 players, got {len(batting_orders)}")

    # Check for uniqueness
    if len(set(batting_orders)) != len(batting_orders):
        raise BadBattingOrder("Batting orders must be unique")

    # Explicitly check that batting orders are exactly 1-9 for defensive programming.
    if sorted(batting_orders) != list(range(1, 10)):
        raise BadBattingOrder("Batting orders must be the numbers 1 through 9, each used exactly once")


def _get(obj, name, default=None):
    """Helper to read either dataclass attributes or dict keys."""
    if obj is None:
        return default
    if hasattr(obj, name):
        return getattr(obj, name)
    if isinstance(obj, dict):
        return obj.get(name, default)
    return default


def validate_data(payload, require_creator: bool = True):
    """Validate the lineup data structure and domain rules.
    
    Only validates - does not fetch or return data.
    Raises domain exceptions if validation fails, returns nothing if valid.
    """
    team_obj = fetch_team_by_id(_get(payload, "team_id"))
    if not team_obj:
        raise TeamNotFound()

    # Extract player ids from input
    ids = []
    for p in _get(payload, "players", []):
        pid = _get(p, "player_id") if not isinstance(p, (int,)) else p
        if pid is None:
            raise PlayersNotFound()
        ids.append(pid)

    # We expect exactly 9 players
    if len(ids) != 9:
        raise PlayersNotFound()

    # Fetch players to validate they exist and belong to correct team
    try:
        players_qs = fetch_players_by_ids(ids)
    except ValueError:
        raise PlayersNotFound()

    # Ensure all players belong to the stated team
    if any(p.team_id != team_obj.id for p in players_qs):
        raise PlayersWrongTeam()

    # Validate creator requirement
    created_by_id = _get(payload, "requested_user_id")
    User = get_user_model()
    if not created_by_id and require_creator:
        # Check that a superuser exists to be used as creator
        created_by_id = User.objects.filter(is_superuser=True).values_list("id", flat=True).first()
        if created_by_id is None:
            raise NoCreator()





def validate_lineup_model(lineup):
    """Validate a Lineup model instance produced by the algorithm.

    Raises the same domain exceptions as the input validator when the
    produced model is invalid. This protects the API from buggy
    algorithm implementations.
    """

    if lineup is None:
        raise PlayersNotFound()

    # Ensure we have a team
    if getattr(lineup, "team_id", None) is None:
        raise PlayersWrongTeam()

    # select_related player to access team_id efficiently
    players = list(lineup.players.select_related("player").all())
    if len(players) == 0:
        raise PlayersNotFound()

    # Check all players belong to the lineup team
    if any(p.player.team_id != lineup.team_id for p in players):
        raise PlayersWrongTeam()

    # Batting order must be unique and consecutive 1..N
    orders = [getattr(p, "batting_order", None) for p in players]
    if None in orders:
        # Algorithm must set batting_order for each player
        raise BadBattingOrder()
    if sorted(orders) != list(range(1, len(orders) + 1)):
        raise BadBattingOrder()

    # All checks passed — return True for convenience
    return True
