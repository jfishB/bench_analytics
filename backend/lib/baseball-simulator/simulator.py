"""
Python script to simulate the offense side of a baseball game,
such that we can compare different lineup possibilities.

by Bram Grooten
"""
from batter import Batter
from baseball import Game
import pandas as pd
import numpy as np
import plotille


def setup_mlb():
    dataset = pd.read_excel("mlb2019.xls", sheet_name=0, header=0)
    # marteke01
    # lemahdj01
    # moncayo01
    # urshegi01
    # reynobr01
    # alvaryo01
    # brantmi02
    lineup_id = [
        'anderti01',
        'bogaexa01',
        'yelicch01',

        'tatisfe02',
        'deverra01',
        'cruzne02',

        'arenano01',
        'blackch02',
        'rendoan01',
        ]
    assert len(lineup_id) == 9
    lineup = []
    for batter_id in lineup_id:
        batter = Batter(player_id=batter_id, dataset=dataset)
        lineup.append(batter)
    return lineup


def setup_own():
    lineup = [
        # probabilities for:    K      out   walk    1B     2B     3B     HR
        Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage1'),
        Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage2'),
        Batter(probabilities=[0.150, 0.400, 0.150, 0.150, 0.045, 0.005, 0.100], name='MikeHomerun'),
        Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage4'),
        Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage5'),
        Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage6'),
        Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage7'),
        Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage8'),
        Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage9'),
    ]
    # Anthony Rendon:
    # strike-out: 0.133  in-play-out: 0.474  walk: 0.124  single: 0.144  double: 0.068	 triple: 0.005 	homerun: 0.053
    return lineup


def play_multiple_lineups(lineups, nr_games=10_000):
    scores = []
    for idx, lineup in enumerate(lineups):
        print(f"\n=== Playing lineup {idx+1}/{len(lineups)} ===")
        avg_score, median_score, std_dev = play_many_games(lineup, nr_games=nr_games, print_stats=False)
        scores.append((avg_score, median_score, std_dev))
    print("\n=== Summary of all lineups ===")
    for idx, stats in enumerate(scores):
        print(f"Lineup {idx+1}: avg_score = {stats[0]:.3f}, median = {stats[1]:.3f}, std_dev = {stats[2]:.3f}")


def make_multiple_lineups_with_one_power_hitter():
    # probabilities for:                 K      out   walk    1B     2B     3B     HR
    batter_avg = Batter(probabilities=[0.150, 0.500, 0.150, 0.150, 0.045, 0.005, 0.000], name='JoeAverage')
    batter_pow = Batter(probabilities=[0.150, 0.400, 0.150, 0.150, 0.045, 0.005, 0.100], name='MikeHomerun')

    # Create 9 lineups with all avg batters except one power hitter at each position
    lineups = []
    for pos in range(9):
        lineup = []
        for i in range(9):
            if i == pos:
                lineup.append(batter_pow)
            else:
                lineup.append(batter_avg)
        lineups.append(lineup)
    return lineups


def play_many_games(lineup, nr_games=10_000, print_stats=True):
    game = Game(lineup, printing=False)
    if print_stats:
        game.print_lineup()

    scores = []
    for game_idx in range(nr_games):
        game.reset_game_state()
        game.play()
        scores.append(game.get_score())
        if (game_idx + 1) % 1000 == 0 and print_stats:
            print(f"Played {game_idx+1} games")

    avg_score = np.mean(scores)
    median_score = np.median(scores)
    std_dev = np.std(scores)
    if print_stats:
        print(f"\nAfter {nr_games} games we have:")
        print(f"avg score: \t{avg_score}")
        print(f"median: \t{median_score}")
        print(f"std dev: \t{std_dev:.2f}")
        print(plotille.hist(scores, bins=int(np.max(scores)), width=50))
    return avg_score, median_score, std_dev


def play_one_game(lineup):
    game = Game(lineup, printing=True)
    game.print_lineup()
    game.reset_game_state()
    game.play()
    score = game.get_score()
    if score == 1:
        print(f"\nThe final score is: 1 run.\n")
    else:
        print(f"\nThe final score is: {score} runs.\n")


if __name__ == '__main__':
    lineup = setup_mlb()
    # lineup = setup_own()

    # play_many_games(lineup, nr_games=10_000)
    play_one_game(lineup)

    ### To figure out the best position for a power hitter:
    # lineups = make_multiple_lineups_with_one_power_hitter()
    # play_multiple_lineups(lineups, nr_games=10_000)
