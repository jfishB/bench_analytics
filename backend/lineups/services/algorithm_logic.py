##########################################
"""
- This file contains the core algorithm
logic for creating batting lineups.
"""
###########################################

from itertools import permutations
from typing import Dict, List

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


# -------- PA scale factor for a given player for a game -------- #
def calculate_player_pa_scale_factor(p: Player, position: int) -> float:
    """Calculate players PA scale factor value with given formula.

    Args:
        p: player in lineup
        position: batting order position (1-9)

    Constants:
        wOBAlg: League average wOBA - From Baseball Savant
        wOBAscale: League wOBA scale - From Fangraphs
        R/PAlg: League average R/PA - From Fangraphs

    Formula:
        Adjusted PA = ((total PA / total games) * PA_MULTIPLIERS[position])
        PA Scale Factor = (Adjusted PA) / (total PA)

    Returns:
        Float value reperesenting the PA Scale factor for this player
    """
    pa_game = 0
    if p.pa is not None and p.b_game is not None and p.b_game > 0:
        pa_game = p.pa / p.b_game
    adjusted_pa = pa_game * PA_MULTIPLIERS[position]
    if p.pa is not None and p.pa > 0:
        scale_factor = adjusted_pa / p.pa
        return scale_factor
    return 0


# -------- Calculate adjusted player metrics to use for BaseRuns formula -------- #
def calculate_player_adjustments(p: Player, position: int, adjustments: Dict[str, float]) -> Dict[str, float]:
    """Calculate given players scaled stats and from there A,B,C,D values to use in BaseRun formula.
        BaseRun Formula and method source: https://library.fangraphs.com/features/baseruns/

    Args:
        p: given player in lineup
        position: batting order position (1-9)
        adjustments: Dict to fill with calculated adjustments

    Returns:
        Dict of float value containg cumulative stat adjustments for the team (updated adjustments list)
        0 - H adjust, 1 - HR adjust, 2 - BB adjust, 3 - IBB adjust, 4 - HBP adjust, 5 - SB adjust, 6 - CS adjust, 7 - GIDP adjust, 8 - SF adjust, 9 - SH adjust, 10 - TB adjust
    """
    pa_scale = calculate_player_pa_scale_factor(p, position)

    # -------- Adjstuing values based on PA scale -------- #
    adjustments["pa_team"] += (
        p.pa * pa_scale
    )  # Getting adjusted PA value for player and adding them all up to get team PA value for 1 game
    adjustments["h_adjust"] += p.hit * pa_scale
    adjustments["hr_adjust"] += p.home_run * pa_scale
    adjustments["bb_adjust"] += p.walk * pa_scale
    adjustments["ibb_adjust"] += p.b_intent_walk * pa_scale
    adjustments["hbp_adjust"] += p.b_hit_by_pitch * pa_scale
    adjustments["sb_adjust"] += p.r_total_stolen_base * pa_scale
    adjustments["cs_adjust"] += p.r_total_caught_stealing * pa_scale
    adjustments["gidp_adjust"] += p.b_gnd_into_dp * pa_scale
    adjustments["sf_adjust"] += p.b_sac_fly * pa_scale
    adjustments["sh_adjust"] += p.b_total_sacrifices * pa_scale
    adjustments["tb_adjust"] += p.b_total_bases * pa_scale

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
        Float value reperesenting the Expected runs scored by given player
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

    # -------- Brute Force Optimization -------- #
    for lineup in permutations(players_list):  # Going through all 9! possible lineups
        # Calculate scores for all available players for this spot
        runs = calculate_player_baserun_values(lineup)  # Expected Runs for current lineup

        best_runs = -999
        best_lineup = None

        if runs > best_runs:
            best_runs = runs
            best_lineup = lineup
    print(best_lineup)
    print("best runs:", best_runs)
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
