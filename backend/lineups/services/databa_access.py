from django.db import transaction
from django.utils import timezone

from lineups.models import Lineup, LineupPlayer
from roster.models import Player, Team


def saving_lineup_to_db(team_obj, players_payload, lineup_name, created_by_id):
    """Save the lineup and its players to the database.

    Expected arguments:
      - team_obj: Team model instance
      - players_payload: list of dicts with keys 'player' (Roster Player model) and 'batting_order' (int)
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
