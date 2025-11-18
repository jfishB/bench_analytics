##########################################
"""
- This file contains the validation logic
- used in views
"""
###########################################

from django.contrib.auth import get_user_model

from roster.models import Player, Team

from .exceptions import BadBattingOrder, NoCreator, PlayersNotFound, PlayersWrongTeam, TeamNotFound
from .input_data import LineupPlayerInput


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
        if hasattr(p, 'batting_order'):
            bo = p.batting_order
        elif isinstance(p, dict):
            bo = p.get('batting_order')
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
    
    # Check that orders cover exactly 1-9
    if sorted(batting_orders) != list(range(1, 10)):
        raise BadBattingOrder("Batting orders must cover positions 1 through 9")


def validate_data(payload):
    """Validate the lineup data for creating a lineup."""

    # Helper to read either dataclass attributes or dict keys
    def _get(obj, name, default=None):
        if obj is None:
            return default
        if hasattr(obj, name):
            return getattr(obj, name)
        if isinstance(obj, dict):
            return obj.get(name, default)
        return default

    team_obj = Team.objects.filter(pk=_get(payload, "team_id")).first()
    if not team_obj:
        raise TeamNotFound()

    # Extract player ids and preserve requested positions from input
    ids = []
    pos_map = {}
    for p in _get(payload, "players", []):
        # support either raw int ids or LineupPlayerInput/dataclass/dict
        pid = _get(p, "player_id") if not isinstance(p, (int,)) else p
        if pid is None:
            raise PlayersNotFound()
        ids.append(pid)
        # capture requested position if present
        pos = _get(p, "position")
        if pos is not None:
            pos_map[pid] = pos

    players_qs = list(Player.objects.filter(id__in=ids).select_related("team"))
    if len(players_qs) != len(ids):
        raise PlayersNotFound()

    # Re-order players to match the input order and attach requested positions
    players_by_id = {p.id: p for p in players_qs}
    ordered_players = []
    for pid in ids:
        player_obj = players_by_id.get(pid)
        if player_obj is None:
            raise PlayersNotFound()
        # attach helper attributes expected by the algorithm
        setattr(player_obj, "player_id", player_obj.id)
        setattr(player_obj, "position", pos_map.get(pid, (player_obj.position or "--")))
        ordered_players.append(player_obj)

    players_qs = ordered_players

    # Ensure all players belong to the stated team
    if any(p.team_id != team_obj.id for p in players_qs):
        raise PlayersWrongTeam()

    # Batting order: optional on input only check if all players have it
    orders = []
    all_orders_present = True
    for p in _get(payload, "players", []):
        bo = _get(p, "batting_order")
        if bo is None:
            all_orders_present = False
            break
        orders.append(bo)

    if all_orders_present:
        if sorted(orders) != list(range(1, len(orders) + 1)):
            raise BadBattingOrder()

    # Determine created_by: prefer provided requested_user_id on payload
    created_by_id = _get(payload, "requested_user_id")
    User = get_user_model()
    if not created_by_id:
        created_by_id = User.objects.filter(is_superuser=True).values_list("id", flat=True).first()
        if created_by_id is None:
            raise NoCreator()

    return {
        "team": team_obj,
        "players": players_qs,
        "created_by_id": created_by_id,
    }


def validate_lineup_model(lineup):
    """Validate a Lineup model instance produced by the algorithm.

    Raises the same domain exceptions as the input validator when the
    produced model is invalid. This protects the API from buggy
    algorithm implementations.
    """
    # Import here to avoid import cycles
    from .exceptions import (
        BadBattingOrder,
        OpponentPitcherNotFound,
        OpponentTeamMismatch,
        PitcherInBatters,
        PlayersNotFound,
        PlayersWrongTeam,
    )

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

    # Opponent pitcher validation (optional)
    opp_pid = getattr(lineup, "opponent_pitcher_id", None)
    if opp_pid is not None:
        # If opponent_team_id is set, it must match the pitcher's team
        opp_team_id = getattr(lineup, "opponent_team_id", None)
        if opp_team_id is not None:
            from roster.models import Player as RosterPlayer

            pitcher = RosterPlayer.objects.filter(pk=opp_pid).first()
            if pitcher and pitcher.team_id != opp_team_id:
                raise OpponentTeamMismatch()

    # All checks passed — return True for convenience
    return True
