"""
Service module for player ranking and WOS calculations.
Separates business logic from views.

NOTE: This is a PLACEHOLDER algorithm.
The ranking logic will be replaced by the algorithm in lineups/services/algorithm_logic.py
"""

from typing import Any, Dict, List, Optional

from roster.models import Player, Team


class PlayerRankingService:
    """Service for player ranking operations."""

    @staticmethod
    def get_ids_sorted_by_woba(player_ids: List[int]) -> List[int]:
        """
        Sort a list of player IDs by their xwoba (descending).

        Args:
            player_ids: List of player IDs to sort

        Returns:
            List of player IDs sorted by xwoba
        """
        if not player_ids:
            return []

        # Fetch players with the given IDs and sort by xwoba descending
        # We use filter(id__in=...) to get the objects, then order_by
        players = Player.objects.filter(id__in=player_ids).order_by("-xwoba")

        # Return the sorted player IDs
        return [player.id for player in players]


def get_all_players_with_stats() -> List[Dict[str, Any]]:
    """
    Fetch all players with a subset of their stats as dictionaries.

    Returns a list of dicts with fields used by downstream placeholder logic.
    """
    return list(
        Player.objects.all().values(
            "id",
            "name",
            "team_id",
            "bb_percent",
            "k_percent",
            "pa",
            "year",
        )
    )


def get_ranked_players(ascending: bool = False, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Placeholder ranking: returns all players with a synthetic `wos_score` field.
    """
    players = get_all_players_with_stats()

    if not players:
        return []

    result: List[Dict[str, Any]] = []
    for player in players:
        player_data = dict(player)
        player_data["wos_score"] = 0.0
        result.append(player_data)

    if top_n:
        result = result[:top_n]

    # sort by wos_score
    result.sort(key=lambda p: p["wos_score"], reverse=not ascending)
    return result


def create_player_with_stats(name: str, **stats) -> Player:
    """
    Create a new player with optional stats.

    Args:
        name: Player name
        **stats: Optional stats fields (xwoba, bb_percent, etc.)

    Returns:
        Created Player instance
    """
    return Player.objects.create(name=name, **stats)


def update_player_stats(player_id: int, **stats) -> Player:
    """
    Update player statistics.

    Args:
        player_id: Player ID
        **stats: Stats fields to update

    Returns:
        Updated Player instance

    Raises:
        Player.DoesNotExist: If player not found
    """
    player = Player.objects.get(id=player_id)

    for field, value in stats.items():
        setattr(player, field, value)

    player.save()
    return player


def get_team_by_id(team_id: int) -> Optional[Team]:
    """
    Retrieve a team by its ID.

    Args:
        team_id: Team ID

    Returns:
        Team instance or None if not found
    """
    try:
        return Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return None
