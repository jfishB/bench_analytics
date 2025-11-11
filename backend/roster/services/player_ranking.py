"""
Service module for player ranking and WOS calculations.
Separates business logic from views.

NOTE: This is a PLACEHOLDER algorithm.
The ranking logic will be replaced by the algorithm in lineups/services/algorithm_logic.py
"""

from typing import Any, Dict, List, Optional

from roster.models import Player, Team


def calculate_wos(player: Dict[str, Any]) -> float:
    """
    Calculate WOS (Weighted On-base Score) for a player.
    
    PLACEHOLDER: This is a simple weighted formula.
    Will be replaced by the algorithm in lineups/services/algorithm_logic.py
    
    Args:
        player: Dictionary with player stats
        
    Returns:
        WOS score as a float
    """
    xwoba = player.get("xwoba") or 0
    bb_percent = player.get("bb_percent") or 0
    k_percent = player.get("k_percent") or 0
    barrel_rate = player.get("barrel_batted_rate") or 0
    
    # Simple weighted formula (placeholder)
    wos = (xwoba * 10) + (bb_percent * 0.5) - (k_percent * 0.3) + (barrel_rate * 0.8)
    return wos


def sort_players_by_wos(players: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
    """
    Sort players by their WOS score.
    
    Args:
        players: List of player dictionaries
        ascending: Sort order (True = lowest first, False = highest first)
        
    Returns:
        Sorted list of players
    """
    return sorted(players, key=lambda p: calculate_wos(p), reverse=not ascending)


def get_all_players_with_stats() -> List[Dict[str, Any]]:
    """
    Fetch all players with their stats as dictionaries.

    Returns:
        List of player dictionaries containing stats.
    """
    return list(
        Player.objects.all().values(
            "id",
            "name",
            "team__name",
            "position",
            "xwoba",
            "bb_percent",
            "k_percent",
            "barrel_batted_rate",
            "pa",
            "year",
        )
    )


def get_ranked_players(ascending: bool = False, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get players ranked by WOS score.

    Args:
        ascending: Sort order (False = highest first)
        top_n: Optional limit on number of results

    Returns:
        List of player dictionaries with wos_score field added.
    """
    players = get_all_players_with_stats()

    if not players:
        return []

    # Sort by WOS
    sorted_players = sort_players_by_wos(players, ascending=ascending)

    # Add WOS score to each player
    result = []
    for player in sorted_players:
        player_data = dict(player)
        player_data["wos_score"] = round(calculate_wos(player), 2)
        result.append(player_data)

    # Apply limit if specified
    if top_n:
        result = result[:top_n]

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
