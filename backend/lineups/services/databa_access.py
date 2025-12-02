"""
- This file defines database access functions for persisting lineups.
- Imported by:
  - backend/lineups/services/lineup_creation_handler.py
  - backend/lineups/services/validator.py
"""

from django.db import transaction
from django.utils import timezone

from lineups.models import Lineup, LineupPlayer
from roster.models import Player
from roster.models import Team
from .utils import get
from django.contrib.auth import get_user_model


def saving_lineup_to_db(team_obj, players_payload, lineup_name, created_by_id):
    """Save the lineup and its players to the database.

    Expected arguments:
      - team_obj: Team model instance
      - players_payload: list of dicts with keys 'player' (Player model) and
      'batting_order' (int)
      - lineup_name: desired name for the created lineup
      - created_by_id: user id who created the lineup
    """

    with transaction.atomic():

        lineup = Lineup.objects.create(
            team=team_obj,
            created_by_id=created_by_id,
            name=lineup_name or f"Lineup {timezone.now().isoformat()}",
        )

        # Create LineupPlayer entries from the provided payload
        lineup_players = []
        for entry in players_payload:
            player = entry.get("player")
            batting_order = entry.get("batting_order")

            lineup_player = LineupPlayer.objects.create(
                lineup=lineup,
                player=player,
                batting_order=batting_order,
            )
            lineup_players.append(lineup_player)

    return lineup, lineup_players


def fetch_players_by_ids(player_ids: list):
    """Fetch players from database by IDs in the specified order.

    Args:
        player_ids: List of player IDs in desired order

    Returns:
        List of Player objects in the same order as player_ids,
        with player_id attribute attached to each player

    Raises:
        ValueError: If any player IDs are not found in database
    """

    players_qs = list(Player.objects.filter(id__in=player_ids)
                      .select_related("team"))

    # Check that we got all requested players
    if len(players_qs) != len(player_ids):
        raise ValueError(f"Expected {len(player_ids)} players, "
                         f"found {len(players_qs)}")

    # Re-order players to match the input order and attach player_id attribute
    players_by_id = {p.id: p for p in players_qs}
    ordered_players = []
    for pid in player_ids:
        player_obj = players_by_id[pid]
        # Attach helper attribute expected by the algorithm
        setattr(player_obj, "player_id", player_obj.id)
        ordered_players.append(player_obj)

    return ordered_players


def fetch_team_by_id(team_id: int):
    """Fetch a team from database by ID.
    Args:
        team_id: The team ID to fetch
    Returns:
        Team object or None if not found
    """

    return Team.objects.filter(pk=team_id).first()


def fetch_lineup_data(payload):
    """Fetch all data needed for lineup creation from database.
    This is a helper function for interactors that need to fetch team,
    players, and creator information after validation.
    Args:
        payload: CreateLineupInput or dict with team_id, players,
        requested_user_id, name
    Returns:
        dict with keys: team, players, created_by_id, name
    """
    # Fetch team
    team_obj = fetch_team_by_id(get(payload, "team_id"))

    # Extract and fetch players
    ids = [get(p, "player_id") if not isinstance(p, (int,)) else p
           for p in get(payload, "players", [])]
    players_qs = fetch_players_by_ids(ids)

    # Get or determine created_by_id
    created_by_id = get(payload, "requested_user_id")
    if not created_by_id:
        User = get_user_model()
        # Try to find a superuser as fallback creator
        created_by_id = User.objects.filter(is_superuser=True).\
            values_list("id", flat=True).first()

    return {
        "team": team_obj,
        "players": players_qs,
        "created_by_id": created_by_id,
        "name": get(payload, "name"),
    }
