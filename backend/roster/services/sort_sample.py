"""Simple sorting utilities for sample data used in the 'simple sorting' ticket.

This module intentionally keeps the implementation small and dependency-free so
it can be used by both Django tests and plain pytest runs.
"""

from typing import List, Any


def simple_sort(items: List[Any]) -> List[Any]:
    """Return a new list containing the sorted items.

    This performs a stable sort using Python's built-in sorted() so it's
    predictable and efficient for typical sample-data sizes.

    Args:
        items: list of comparable items (numbers, strings, or dicts with keys)

    Returns:
        A new list with items in ascending order.
    """
    if items is None:
        raise ValueError("items must be a list, got None")
    return sorted(items)


def sort_by_key(items: List[dict], key: str, reverse: bool = False) -> List[dict]:
    """Sort a list of dictionaries by the provided key.

    Missing keys will be treated as None and sorted accordingly.
    """
    if items is None:
        raise ValueError("items must be a list, got None")
    return sorted(items, key=lambda d: d.get(key), reverse=reverse)


def calculate_wos(player: dict) -> float:
    """Calculate Weighted Offensive Score (WOS) for a player.

    Formula:
        WOS = 1000 * xwOBA + 2 * BB% + Barrel% - 0.5 * K%

    Args:
        player: dictionary containing player stats with keys:
            - xwoba: expected weighted on-base average (0.0-1.0)
            - bb_percent: walk rate (0-100)
            - barrel_batted_rate: ideal contact rate (0-100)
            - k_percent: strikeout rate (0-100)

    Returns:
        WOS score (float). Returns 0.0 if required fields are missing.
    """
    xwoba = player.get('xwoba', 0) or 0
    bb_percent = player.get('bb_percent', 0) or 0
    barrel_rate = player.get('barrel_batted_rate', 0) or 0
    k_percent = player.get('k_percent', 0) or 0

    wos = (1000 * xwoba) + (2 * bb_percent) + barrel_rate - (0.5 * k_percent)
    return wos


def sort_players_by_wos(players: List[dict], ascending: bool = False) -> List[dict]:
    """Sort players by Weighted Offensive Score (WOS).

    Args:
        players: list of player dictionaries containing offensive stats
        ascending: if True, sort from lowest to highest WOS; default False (highest first)

    Returns:
        List of players sorted by WOS score.
    """
    if players is None:
        raise ValueError("players must be a list, got None")
    
    return sorted(players, key=lambda p: calculate_wos(p), reverse=not ascending)
