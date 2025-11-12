##########################################
"""
- This file contains the validation logic
- used in views
"""
###########################################

from django.contrib.auth import get_user_model

from roster.models import Player, Team

from .exceptions import (
    BadBattingOrder,
    NoCreator,
    PlayersNotFound,
    PlayersWrongTeam,
    TeamNotFound,
)


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

    # Extract player ids from input (supports dataclass list or list of dicts)
    ids = []
    for p in _get(payload, "players", []):
        pid = _get(p, "player_id") if not isinstance(p, (int,)) else p
        if pid is None:
            raise PlayersNotFound()
        ids.append(pid)

    players_qs = list(Player.objects.filter(id__in=ids).select_related("team"))
    if len(players_qs) != len(ids):
        raise PlayersNotFound()

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
        created_by_id = (
            User.objects.filter(is_superuser=True).values_list("id", flat=True).first()
        )
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

    # All checks passed — return True for convenience
    return True
