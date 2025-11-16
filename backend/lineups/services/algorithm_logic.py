##########################################
"""
- This file contains the core algorithm
logic for creating batting lineups.
"""
###########################################

from typing import Dict, List
from itertools import permutations

from django.contrib.auth import get_user_model
from django.db import transaction

from lineups.models import Lineup, LineupPlayer
from lineups.services.validator import validate_data
from roster.models import Player

# -------- Batting Spot PA% Multipliers -------- # Source https://www.bluebirdbanter.com/2012/10/12/3490578/lineup-optimization-part-1-of-2?utm_source and https://www.insidethebook.com/ {Page 128}
PA_MULTIPLIERS = {
    1: 1.10,
    2: 1.075,
    3: 1.05,
    4: 1.025,
    5: 1.00,
    6: 0.975,
    7: 0.95,
    8: 0.925,
    9: 0.90,
}

# -------- League Averages for R/PA Calculation -------- #
WOBA_LEAGUE_AVG = 0.313  # League average wOBA # Source: Baseball Savant https://baseballsavant.mlb.com/leaderboard/expected_statistics
WOBA_SCALE = 1.232  # League wOBA scale # Source: Fangraphs https://www.fangraphs.com/tools/guts?type=cn
RPA_LEAGUE_AVG = 0.118  # League average RPA # Source: Fangraphs https://www.fangraphs.com/tools/guts?type=cn


def calculate_player_rpa(players_list: List[Player]) -> Dict[Player, float]:
    """Calculate each players R/PA with given formula.

    Args:
        players_list: List of 9 players in lineup
    
    Constants:
        wOBAlg: League average wOBA - From Baseball Savant
        wOBAscale: League wOBA scale - From Fangraphs
        R/PAlg: League average R/PA - From Fangraphs

    Formula:
        R/PA(p) = ((wOBA(p) - wOBA(lg)) / wOBAscale) + R/PA(lg) 

    Returns:
        Dictionary mapping index(player) to R/PA value(float)
    """
    player_rpas = {}
    for Player in players_list:
        if Player.woba is not None and Player.pa is not None and Player.pa > 0:
            rpa = ((Player.woba - WOBA_LEAGUE_AVG) / WOBA_SCALE) + RPA_LEAGUE_AVG  # See formula above
            player_rpas[Player] = rpa
        else:
            player_rpas[Player] = 0.0  # Default R/PA for players with no data
    return player_rpas

# -------- Expected Runs for a Given Lineup -------- #
def compute_expected_runs(lineup: tuple[Player], player_rpas: Dict[Player, float]) -> float:
    """
    Args:
        players_list: List of 9 players in lineup

    Constants:
        PA_MULTIPLIERS: Dict mapping batting spot to PA multiplier 

    Returns:
        Expected run count for given lineup as a float
    """
    total_runs = 0.0

    for id, player in enumerate(lineup):
        spot = id + 1

        player_rpa = player_rpas[player]
        weight = PA_MULTIPLIERS[spot]

        total_runs += player_rpa * weight

    return total_runs


def algorithm_create_lineup(payload):
    """Create a batting lineup based on the provided payload.

    This function contains the core logic for creating a batting lineup.
    It validates the input data, applies the lineup algorithm, and returns
    the created lineup.

    Args:
        payload (CreateLineupInput): The input data for creating the lineup.

    Returns:
        Lineup: The created Lineup model instance with assigned batting orders.
    """
    # Validate and get processed data
    validated = validate_data(payload)
    team_obj = validated["team"]
    players_list = validated["players"]
    created_by_id = validated["created_by_id"]

    # Build position mapping from payload
    position_map = {p.player_id: p.position for p in players_list}

    # -------- R/PA Calculation -------- #
    player_rpas = calculate_player_rpa(players_list)

    # -------- Brute Force Optimization -------- #
    for lineup in permutations(players_list):  # Going through all 9! possible lineups
        # Calculate scores for all available players for this spot
        runs = compute_expected_runs(lineup, player_rpas)

        best_runs = -999
        best_lineup = None

        if runs > best_runs:
            best_runs = runs
            best_lineup = lineup
    print(best_lineup)
    print('best runs:', best_runs)
    # Create the Lineup and LineupPlayer objects in a transaction
    # TODO: seperate for clean architecture
    with transaction.atomic():
        User = get_user_model()
        created_by = User.objects.get(pk=created_by_id)

        lineup = Lineup.objects.create(
            team=team_obj,
            created_by=created_by,
        )

        # Create LineupPlayer entries
        lineup_players = []
        for i in range(0, len(best_lineup)):
            player = best_lineup[i]
            position = position_map.get(player.id, player.position)

            lineup_player = LineupPlayer.objects.create(
                lineup=lineup,
                player=player,
                position=position,
                batting_order=i + 1,
            )
            lineup_players.append(lineup_player)

    return lineup, lineup_players