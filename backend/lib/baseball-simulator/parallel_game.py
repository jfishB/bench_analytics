"""
Parallel game simulator using multiprocessing for performance.
Splits game simulations across multiple CPU cores for ~4x speedup on 4-core machines.
"""

import multiprocessing as mp
from functools import partial
import numpy as np
from baseball import Game


def play_single_game(lineup, game_params):
    """
    Play a single game with the given lineup.
    
    Args:
        lineup: List of Batter objects
        game_params: Dictionary of game parameters
    
    Returns:
        int: Final score of the game
    """
    game = Game(lineup, printing=False, **game_params)
    game.reset_game_state()
    game.play()
    return game.get_score()


def play_games_chunk(args):
    """
    Play a chunk of games (worker function for multiprocessing).
    
    Args:
        args: Tuple of (lineup, num_games, game_params)
    
    Returns:
        list: Scores from all games in this chunk
    """
    lineup, num_games, game_params = args
    scores = []
    for _ in range(num_games):
        score = play_single_game(lineup, game_params)
        scores.append(score)
    return scores


class ParallelGame:
    """
    Runs baseball game simulations in parallel across multiple CPU cores.
    """
    
    def __init__(
        self,
        lineup,
        num_games=10000,
        nr_innings=9,
        prob_advance_runner_on_out=0.2,
        prob_double_play=0.4,
        prob_steal_2nd_base=0.05,
        prob_steal_3rd_base=0.01,
        prob_steal_home=0.001,
        prob_1st_to_3rd=0.2,
        prob_score_from_2nd_on_single=0.5,
        prob_score_from_1st_on_double=0.3,
        num_processes=None,
    ):
        """
        Initialize parallel game simulator.
        
        Args:
            lineup: List of 9 Batter objects
            num_games: Total number of games to simulate
            nr_innings: Number of innings per game (default 9)
            prob_*: Various probability parameters for game events
            num_processes: Number of CPU cores to use (None = use all available)
        """
        self.lineup = lineup
        self.num_games = num_games
        
        # Store game parameters
        self.game_params = {
            'nr_innings': nr_innings,
            'prob_advance_runner_on_out': prob_advance_runner_on_out,
            'prob_double_play': prob_double_play,
            'prob_steal_2nd_base': prob_steal_2nd_base,
            'prob_steal_3rd_base': prob_steal_3rd_base,
            'prob_steal_home': prob_steal_home,
            'prob_1st_to_3rd': prob_1st_to_3rd,
            'prob_score_from_2nd_on_single': prob_score_from_2nd_on_single,
            'prob_score_from_1st_on_double': prob_score_from_1st_on_double,
        }
        
        # Determine number of processes to use
        if num_processes is None:
            self.num_processes = mp.cpu_count()
        else:
            self.num_processes = num_processes
        
        # Store scores after playing
        self.scores = None
    
    def play(self):
        """
        Run all game simulations in parallel across multiple CPU cores.
        """
        # Split games into chunks for each process
        games_per_process = self.num_games // self.num_processes
        remainder = self.num_games % self.num_processes
        
        # Create chunks with sizes as even as possible
        chunks = []
        for i in range(self.num_processes):
            chunk_size = games_per_process + (1 if i < remainder else 0)
            if chunk_size > 0:
                chunks.append((self.lineup, chunk_size, self.game_params))
        
        # Run simulations in parallel
        with mp.Pool(processes=len(chunks)) as pool:
            results = pool.map(play_games_chunk, chunks)
        
        # Flatten results into single list
        self.scores = []
        for chunk_scores in results:
            self.scores.extend(chunk_scores)
    
    def get_scores(self):
        """
        Get list of all game scores.
        
        Returns:
            list: Scores from all simulated games
        """
        if self.scores is None:
            raise RuntimeError("Must call play() before get_scores()")
        return self.scores


def play_many_games_parallel(lineup, num_games=10000, num_processes=None, **game_params):
    """
    Convenience function to run parallel game simulations.
    
    Args:
        lineup: List of 9 Batter objects
        num_games: Number of games to simulate
        num_processes: Number of CPU cores to use (None = use all)
        **game_params: Additional game parameters
    
    Returns:
        tuple: (avg_score, median_score, std_dev, all_scores)
    """
    game = ParallelGame(
        lineup=lineup,
        num_games=num_games,
        num_processes=num_processes,
        **game_params
    )
    game.play()
    scores = game.get_scores()
    
    avg_score = np.mean(scores)
    median_score = np.median(scores)
    std_dev = np.std(scores)
    
    return avg_score, median_score, std_dev, scores

