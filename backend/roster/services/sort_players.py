"""Service utilities previously implemented as a management command.

Expose a function to compute and return the sorted players by WOS so callers
can print, test or re-use the results.
"""
from typing import List
from roster.models import Player
from .sort_sample import sort_players_by_wos, calculate_wos


def get_sorted_players(top: int = 10, ascending: bool = False) -> List[dict]:
    """Return top N players sorted by WOS as a list of dicts.

Each dict contains the fields selected from the DB query, plus a computed
WOS score key where needed.
"""
    players = Player.objects.all().values(
        "name", "savant_player_id", "xwoba", "bb_percent", "barrel_batted_rate", "k_percent"
    )
    players_list = list(players)
    if not players_list:
        return []

    sorted_players = sort_players_by_wos(players_list, ascending=ascending)
    # add computed wos
    out = []
    for p in sorted_players[:top]:
        row = dict(p)
        row["wos_score"] = calculate_wos(p)
        out.append(row)
    return out
