##########################################
"""
- This file contains the core algorithm
logic for creating batting lineups.
"""
###########################################

from itertools import permutations
from typing import Dict

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


# -------- Calculate adjusted player metrics to use for BaseRuns formula -------- #
def calculate_player_adjustments(p: Player, position: int, adjustments: Dict[str, float]) -> Dict[str, float]:
    """Calculate given players scaled stats and from there A,B,C,D values to use in BaseRun formula.
        BaseRun Formula and method source: https://library.fangraphs.com/features/baseruns/

    Args:
        p: given player in lineup
        position: batting order position (1-9)
        adjustments: Dict to fill with calculated adjustments

    Formula:
        PA Scale Factor = (PA Multipier based on position) / (total games)

    Returns:
        Dict of float value containg cumulative stat adjustments for the team (updated adjustments list)
        0 - H adjust, 1 - HR adjust, 2 - BB adjust, 3 - IBB adjust, 4 - HBP adjust, 5 - SB adjust, 6 - CS adjust, 7 - GIDP adjust, 8 - SF adjust, 9 - SH adjust, 10 - TB adjust
    """
    if p.b_game is None or p.b_game == 0:
        return adjustments
    pa_scale = (
        PA_MULTIPLIERS[position] / p.b_game
    )  # Since the stats we will be adjusting are all season long we need to divide by the number of games the player played to get game average stats

    # -------- Adjusting values based on PA scale -------- #
    adjustments["pa_team"] += (
        p.pa or 0
    ) * pa_scale  # Getting adjusted PA value for player and adding them all up to get team PA value for 1 game
    adjustments["h_adjust"] += (p.hit or 0) * pa_scale
    adjustments["hr_adjust"] += (p.home_run or 0) * pa_scale
    adjustments["bb_adjust"] += (p.walk or 0) * pa_scale
    adjustments["ibb_adjust"] += (p.b_intent_walk or 0) * pa_scale
    adjustments["hbp_adjust"] += (p.b_hit_by_pitch or 0) * pa_scale
    adjustments["sb_adjust"] += (p.r_total_stolen_base or 0) * pa_scale
    adjustments["cs_adjust"] += (p.r_total_caught_stealing or 0) * pa_scale
    adjustments["gidp_adjust"] += (p.b_gnd_into_dp or 0) * pa_scale
    adjustments["sf_adjust"] += (p.b_sac_fly or 0) * pa_scale
    # Use the model's sacrifice bunt field (SH)
    adjustments["sh_adjust"] += (p.b_sac_bunt or 0) * pa_scale
    adjustments["tb_adjust"] += (p.b_total_bases or 0) * pa_scale

    return adjustments


# -------- BaseRun formula to calculate lineups expected runs for a game -------- #
def calculate_player_baserun_values(lineup: tuple[Player]) -> float:
    """Calculate given players scaled stats and from there A,B,C,D values to use in BaseRun formula.
        BaseRun Formula and method source: https://library.fangraphs.com/features/baseruns/

    Args:
        lineup: lineup of 9 players

    Value Meanings and Calculations:
        A: Base runners = H + BB + HBP - (0.5*IBB) - HR
        B: Runner advancement = 1.1*[1.4*TB - 0.6*H - 3*HR + 0.1*(BB + HBP - IBB) + 0.9*(SB - CS - GDP)]
        C: Outs = PAadjust - BB - SF - SH - HBP - H + CS + GDP
        D: Home runs = HR

    Formula:
        BaseRun = [(A*B) / (B + C)] + D

    Returns:
        Float value representing the Expected runs scored by given player
    """
    adjustments = {
        "pa_team": 0.0,
        "h_adjust": 0.0,
        "hr_adjust": 0.0,
        "bb_adjust": 0.0,
        "ibb_adjust": 0.0,
        "hbp_adjust": 0.0,
        "sb_adjust": 0.0,
        "cs_adjust": 0.0,
        "gidp_adjust": 0.0,
        "sf_adjust": 0.0,
        "sh_adjust": 0.0,
        "tb_adjust": 0.0,
    }

    for id, p in enumerate(lineup):
        spot = id + 1
        adjustments = calculate_player_adjustments(p, spot, adjustments)

    # -------- Calculating BaseRun formula inputs -------- #
    a = (
        adjustments["h_adjust"]
        + adjustments["bb_adjust"]
        + adjustments["hbp_adjust"]
        - (0.5 * adjustments["ibb_adjust"])
        - adjustments["hr_adjust"]
    )
    b = 1.1 * (
        1.4 * adjustments["tb_adjust"]
        - 0.6 * adjustments["h_adjust"]
        - 3 * adjustments["hr_adjust"]
        + 0.1 * (adjustments["bb_adjust"] + adjustments["hbp_adjust"] - adjustments["ibb_adjust"])
        + 0.9 * (adjustments["sb_adjust"] - adjustments["cs_adjust"] - adjustments["gidp_adjust"])
    )
    c = (
        adjustments["pa_team"]
        - adjustments["bb_adjust"]
        - adjustments["sf_adjust"]
        - adjustments["sh_adjust"]
        - adjustments["hbp_adjust"]
        - adjustments["h_adjust"]
        + adjustments["cs_adjust"]
        + adjustments["gidp_adjust"]
    )  # (pa_scale * p.pa) - to get PA_adjust back. We dont want to use native PA since that is entire season PA and we are calculating for 1 game
    d = adjustments["hr_adjust"]

    # -------- BaseRun Calculation -------- #
    if (b + c) > 0:
        expected_runs = ((a * b) / (b + c)) + d
        return expected_runs

    return 0


def algorithm_create_lineup(payload) -> tuple[Player]:
    """Create a batting lineup based on the provided payload.

    This function contains the core logic for creating a batting lineup.
    It validates the input data, applies the lineup algorithm, and returns
    the created lineup.

    Args:
        payload (CreateLineupInput): The input data for creating the lineup.

    Returns:
        Lineup: The created Lineup model instance with assigned batting orders.
    """
    # Validate and get processed data (algorithm generation doesn't require a creator)
    validated = validate_data(payload, require_creator=False)
    players_list = validated["players"]
    best_runs = -float("inf")
    best_lineup = None

    # -------- Brute Force Optimization -------- #
    for lineup in permutations(players_list):  # Going through all 9! possible lineups
        # Calculate scores for all available players for this spot
        runs = calculate_player_baserun_values(lineup)  # Expected Runs for current lineup

        if runs > best_runs:
            best_runs = runs
            best_lineup = lineup
    # Return the best lineup found (tuple of Player instances)
    # If no lineup was computed, return an empty tuple to indicate no result
    if best_lineup is None:
        return tuple()

    return best_lineup