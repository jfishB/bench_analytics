"""
fetches player data from database and converts to simulation format.
queries roster.models.Player using django orm, maintains player order,
and converts to batterstats dtos for simulation.
called by views.py to get player data before running simulations.
uses dto.py for batterstats structure.
"""

from typing import List

from .dto import BatterStats


class PlayerService:
    """Service for fetching player data and converting to simulation DTOs."""

    def __init__(self):
        # Import here to avoid circular dependencies
        from roster.models import Player

        self.Player = Player

    def get_players_by_ids(self, player_ids: List[int]) -> List[BatterStats]:
        """
        Fetch players by their IDs and convert to BatterStats.

        Args:
            player_ids: List of player primary keys

        Returns:
            List of BatterStats in the same order as player_ids

        Raises:
            ValueError: If any player is not found or missing required stats
        """
        players = self.Player.objects.filter(id__in=player_ids)

        # Create a lookup dict to maintain order
        player_dict = {p.id: p for p in players}

        # Check all players were found
        missing = set(player_ids) - set(player_dict.keys())
        if missing:
            raise ValueError(f"Players not found: {missing}")

        # Convert to BatterStats in the requested order
        batter_stats = []
        for player_id in player_ids:
            player = player_dict[player_id]
            stats = self._convert_to_batter_stats(player)
            batter_stats.append(stats)

        return batter_stats

    def get_players_by_names(self, names: List[str]) -> List[BatterStats]:
        """
        Fetch players by their names.

        Args:
            names: List of player names (must match exactly)

        Returns:
            List of BatterStats in the same order as names
        """
        players = self.Player.objects.filter(name__in=names)

        player_dict = {p.name: p for p in players}

        missing = set(names) - set(player_dict.keys())
        if missing:
            raise ValueError(f"Players not found: {missing}")

        batter_stats = []
        for name in names:
            player = player_dict[name]
            stats = self._convert_to_batter_stats(player)
            batter_stats.append(stats)

        return batter_stats

    def get_team_players(self, team_id: int, limit: int = 9) -> List[BatterStats]:
        """
        Get players from a specific team, ordered by plate appearances.

        Args:
            team_id: Team ID
            limit: Maximum number of players to return (default 9)

        Returns:
            List of BatterStats for top players by PA
        """
        players = self.Player.objects.filter(team_id=team_id).order_by("-pa")[:limit]

        if not players:
            raise ValueError(f"No players found for team {team_id}")

        return [self._convert_to_batter_stats(p) for p in players]

    def _convert_to_batter_stats(self, player) -> BatterStats:
        """
        Convert a Player model instance to a BatterStats domain entity.

        Extracts the raw counting stats needed for simulation.
        """
        pa = player.pa or 0
        if pa == 0:
            raise ValueError(f"Player {player.name} has no plate appearances")

        # Use the raw counting stats from the model
        return BatterStats(
            name=player.name,
            plate_appearances=pa,
            hits=player.hit or 0,
            doubles=player.double or 0,
            triples=player.triple or 0,
            home_runs=player.home_run or 0,
            strikeouts=player.strikeout or 0,
            walks=player.walk or 0,
        )
