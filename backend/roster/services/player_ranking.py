"""
Service module for player ranking and WOS calculations.
Separates business logic from views.
"""
from typing import List, Dict, Any
from roster.models import Player
from .sort_sample import calculate_wos, sort_players_by_wos


def get_all_players_with_stats() -> List[Dict[str, Any]]:
    """
    Fetch all players with their stats as dictionaries.
    
    Returns:
        List of player dictionaries containing stats.
    """
    return list(
        Player.objects.all().values(
            "id", "name", "team__name", "position",
            "xwoba", "bb_percent", "k_percent", 
            "barrel_batted_rate", "pa", "year"
        )
    )


def get_ranked_players(ascending: bool = False, top_n: int | None = None) -> List[Dict[str, Any]]:
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
        if hasattr(player, field):
            setattr(player, field, value)
    
    player.save()
    return player
