import numpy as np


class VectorizedGame:
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
    ):
        self.lineup = lineup
        self.num_games = num_games
        self.nr_innings = nr_innings

        # Probabilities
        self.prob_advance_runner_on_out = prob_advance_runner_on_out
        self.prob_double_play = prob_double_play
        self.prob_steal_2nd_base = prob_steal_2nd_base
        self.prob_steal_3rd_base = prob_steal_3rd_base
        self.prob_steal_home = prob_steal_home
        self.prob_1st_to_3rd = prob_1st_to_3rd
        self.prob_score_from_2nd_on_single = prob_score_from_2nd_on_single
        self.prob_score_from_1st_on_double = prob_score_from_1st_on_double

        # Pre-compute lineup probabilities matrix (9 batters x 7 outcomes)
        # Outcomes: 0:SO, 1:Out, 2:BB, 3:1B, 4:2B, 5:3B, 6:HR
        self.lineup_probs = np.array([b.probs for b in lineup])

        # Game State
        self.scores = np.zeros(num_games, dtype=int)
        self.outs = np.zeros(num_games, dtype=int)
        self.batter_up = np.zeros(num_games, dtype=int)
        self.on_1b = np.zeros(num_games, dtype=bool)
        self.on_2b = np.zeros(num_games, dtype=bool)
        self.on_3b = np.zeros(num_games, dtype=bool)
        self.innings = np.zeros(num_games, dtype=int)
        self.game_over = np.zeros(num_games, dtype=bool)

    def play(self):
        # Loop until all games are over
        # We can optimize by looping through innings

        # To avoid infinite loops or overly complex logic, we'll simulate "steps"
        # A step is one plate appearance for all active games

        while not np.all(self.game_over):
            # Identify active games (not over)
            active_mask = ~self.game_over
            if not np.any(active_mask):
                break

            # Check for inning changes for active games
            # If outs >= 3, move to next inning
            inning_change_mask = active_mask & (self.outs >= 3)
            if np.any(inning_change_mask):
                self.innings[inning_change_mask] += 1
                self.outs[inning_change_mask] = 0
                self.on_1b[inning_change_mask] = False
                self.on_2b[inning_change_mask] = False
                self.on_3b[inning_change_mask] = False

                # Check if game over after inning change
                game_over_mask = inning_change_mask & (self.innings >= self.nr_innings)
                self.game_over[game_over_mask] = True

                # Update active mask after finishing games
                active_mask = ~self.game_over
                if not np.any(active_mask):
                    break

            # Now process plate appearances for truly active games (outs < 3)
            # Note: Some games might have just switched innings and have 0 outs now.

            # Steal attempts (before pitch)
            # Only for games with runners and < 3 outs
            # We'll simplify and do steals for all active games with runners
            # Steal 2nd
            steal_2_mask = active_mask & self.on_1b & ~self.on_2b
            if np.any(steal_2_mask):
                r = np.random.rand(np.count_nonzero(steal_2_mask))
                success = r < self.prob_steal_2nd_base
                # Success: 1B -> 2B
                # Fail: 1B -> Out
                # We need to map back to full array indices
                indices = np.where(steal_2_mask)[0]
                success_indices = indices[success]
                fail_indices = indices[~success]

                self.on_1b[success_indices] = False
                self.on_2b[success_indices] = True

                self.on_1b[fail_indices] = False
                self.outs[fail_indices] += 1
                # If out caused 3 outs, we stop processing this game for this step?
                # Yes, but for vectorization simplicity, we might continue to the pitch
                # if we don't check outs immediately.
                # But standard baseball: if caught stealing for 3rd out, inning ends.
                # So we should re-check active/outs status after steals.

            # Steal 3rd
            steal_3_mask = active_mask & self.on_2b & ~self.on_3b & (self.outs < 3)
            if np.any(steal_3_mask):
                r = np.random.rand(np.count_nonzero(steal_3_mask))
                success = r < self.prob_steal_3rd_base
                indices = np.where(steal_3_mask)[0]
                success_indices = indices[success]
                fail_indices = indices[~success]

                self.on_2b[success_indices] = False
                self.on_3b[success_indices] = True

                self.on_2b[fail_indices] = False
                self.outs[fail_indices] += 1

            # Steal Home
            steal_h_mask = active_mask & self.on_3b & (self.outs < 3)
            if np.any(steal_h_mask):
                r = np.random.rand(np.count_nonzero(steal_h_mask))
                success = r < self.prob_steal_home
                indices = np.where(steal_h_mask)[0]
                success_indices = indices[success]
                fail_indices = indices[~success]

                self.on_3b[success_indices] = False
                self.scores[success_indices] += 1

                self.on_3b[fail_indices] = False
                self.outs[fail_indices] += 1

            # Re-evaluate active games for batting (must have < 3 outs)
            batting_mask = active_mask & (self.outs < 3)
            if not np.any(batting_mask):
                continue

            # Get current batter probabilities
            current_batters = self.batter_up[batting_mask]
            probs = self.lineup_probs[current_batters]  # (N_active, 7)

            # Generate outcomes
            cum_probs = probs.cumsum(axis=1)
            r = np.random.rand(len(current_batters), 1)
            outcomes = (r < cum_probs).argmax(axis=1)  # 0..6

            # Map outcomes to full array indices
            indices = np.where(batting_mask)[0]

            # 0: Strike-out
            so_mask = outcomes == 0
            self.outs[indices[so_mask]] += 1

            # 1: In-play-out
            ipo_mask = outcomes == 1
            ipo_indices = indices[ipo_mask]
            self.outs[ipo_indices] += 1

            # Advance runners on out?
            # Logic from original:
            # if outs < 3:
            #   if 2nd: 20% advance to 3rd
            #   if 3rd: 20% score
            # Note: original code checks outs AFTER incrementing. So if now 3 outs, no advance.
            # But here we just incremented outs.
            # We need to check if outs < 3 for these games.
            valid_advance_mask = ipo_indices[self.outs[ipo_indices] < 3]
            if len(valid_advance_mask) > 0:
                # Runner on 2nd -> 3rd
                r2 = np.random.rand(len(valid_advance_mask))
                advance_2_3 = (
                    (r2 < self.prob_advance_runner_on_out) & self.on_2b[valid_advance_mask] & ~self.on_3b[valid_advance_mask]
                )
                # We need to be careful with indices mapping again.
                # Let's do it simpler: iterate masks on the full array

                # Create a mask for games that had in-play-out AND are still active (outs < 3)
                ipo_active_mask = np.zeros(self.num_games, dtype=bool)
                ipo_active_mask[valid_advance_mask] = True

                # 2nd to 3rd
                r_adv = np.random.rand(self.num_games)
                adv_2_3 = ipo_active_mask & self.on_2b & ~self.on_3b & (r_adv < self.prob_advance_runner_on_out)
                self.on_2b[adv_2_3] = False
                self.on_3b[adv_2_3] = True

                # 3rd scores (Sacrifice fly/groundout)
                # Original: if 3rd base: score (prob_advance_runner_on_out)
                adv_3_h = ipo_active_mask & self.on_3b & (r_adv < self.prob_advance_runner_on_out)
                self.on_3b[adv_3_h] = False
                self.scores[adv_3_h] += 1

                # Double play logic
                # If 1st base occupied and < 3 outs (after first out), chance for double play
                # Original: if 1st base: prob_double_play -> outs+=1, 1st base=False
                # Note: we already added 1 out. So if outs was 0 or 1, we can have double play.
                # If outs is now 3, no double play (inning over).
                dp_candidates = ipo_active_mask & self.on_1b & (self.outs < 3)
                r_dp = np.random.rand(self.num_games)
                is_dp = dp_candidates & (r_dp < self.prob_double_play)

                self.outs[is_dp] += 1
                self.on_1b[is_dp] = False
                # If double play, runner on 2nd/3rd usually doesn't advance?
                # Original code: "Runner on 1st out. Runner on 2nd stays? Runner on 3rd scores?"
                # Original code `in_play_out` is complex.
                # It iterates runners.
                # Let's stick to the simplified logic or try to match closer if needed.
                # Original:
                # if 1st: if double_play: outs+=1, 1st=False. else: 1st->2nd (advance prob)? No.
                # The original code for `in_play_out` advances runners with `prob_advance_runner_on_out`.
                # It handles double play separately.

            # 2: Walk
            bb_mask = outcomes == 2
            bb_indices = indices[bb_mask]
            # Logic: 1st=True. If 1st was True, 2nd=True. If 2nd was True, 3rd=True. If 3rd was True, Score.
            # We can do this by shifting.
            # Forced advance.
            # 3rd scores if 1st, 2nd, 3rd all occupied
            score_mask = self.on_1b[bb_indices] & self.on_2b[bb_indices] & self.on_3b[bb_indices]
            self.scores[bb_indices[score_mask]] += 1

            # 3rd occupied if 1st & 2nd occupied (regardless of previous 3rd, it stays occupied)
            self.on_3b[bb_indices] = self.on_3b[bb_indices] | (self.on_1b[bb_indices] & self.on_2b[bb_indices])

            # 2nd occupied if 1st occupied
            self.on_2b[bb_indices] = self.on_2b[bb_indices] | self.on_1b[bb_indices]

            # 1st always occupied
            self.on_1b[bb_indices] = True

            # 3: Single
            s_mask = outcomes == 3
            s_indices = indices[s_mask]

            # 3rd scores - only clear if runner was there
            runner_on_3rd_mask = self.on_3b[s_indices]
            if np.any(runner_on_3rd_mask):
                score_3rd_indices = s_indices[runner_on_3rd_mask]
                self.scores[score_3rd_indices] += 1
                self.on_3b[score_3rd_indices] = False

            # 2nd scores (50%) or to 3rd - only for games with runner on 2nd
            mask_2nd = self.on_2b[s_indices]
            if np.any(mask_2nd):
                # We need random decisions for the subset
                subset_indices = s_indices[mask_2nd]
                r_s = np.random.rand(len(subset_indices))
                score_from_2 = r_s < self.prob_score_from_2nd_on_single

                score_indices = subset_indices[score_from_2]
                third_indices = subset_indices[~score_from_2]

                self.scores[score_indices] += 1
                self.on_3b[third_indices] = True
                self.on_2b[subset_indices] = False  # Cleared from 2nd

            # 1st to 2nd (80%) or 3rd (20%) - only for games with runner on 1st
            mask_1st = self.on_1b[s_indices]
            if np.any(mask_1st):
                subset_indices = s_indices[mask_1st]
                r_s = np.random.rand(len(subset_indices))
                to_3rd = r_s < self.prob_1st_to_3rd

                to_3rd_indices = subset_indices[to_3rd]
                to_2nd_indices = subset_indices[~to_3rd]

                self.on_3b[to_3rd_indices] = True
                self.on_2b[to_2nd_indices] = True
                self.on_1b[subset_indices] = False

            # Batter to 1st
            self.on_1b[s_indices] = True

            # 4: Double
            d_mask = outcomes == 4
            d_indices = indices[d_mask]

            # 3rd scores - only clear if runner was there
            runner_on_3rd_mask = self.on_3b[d_indices]
            if np.any(runner_on_3rd_mask):
                score_3rd_indices = d_indices[runner_on_3rd_mask]
                self.scores[score_3rd_indices] += 1
                self.on_3b[score_3rd_indices] = False

            # 2nd scores - only clear if runner was there
            runner_on_2nd_mask = self.on_2b[d_indices]
            if np.any(runner_on_2nd_mask):
                score_2nd_indices = d_indices[runner_on_2nd_mask]
                self.scores[score_2nd_indices] += 1
                self.on_2b[score_2nd_indices] = False

            # 1st scores (30%) or to 3rd - only for games with runner on 1st
            mask_1st = self.on_1b[d_indices]
            if np.any(mask_1st):
                subset_indices = d_indices[mask_1st]
                r_d = np.random.rand(len(subset_indices))
                score_from_1 = r_d < self.prob_score_from_1st_on_double

                score_indices = subset_indices[score_from_1]
                third_indices = subset_indices[~score_from_1]

                self.scores[score_indices] += 1
                self.on_3b[third_indices] = True
                self.on_1b[subset_indices] = False

            # Batter to 2nd
            self.on_2b[d_indices] = True

            # 5: Triple
            t_mask = outcomes == 5
            t_indices = indices[t_mask]

            # All runners score - clear each base only if occupied
            # 3rd base runner scores
            runner_on_3rd_mask = self.on_3b[t_indices]
            if np.any(runner_on_3rd_mask):
                score_3rd_indices = t_indices[runner_on_3rd_mask]
                self.scores[score_3rd_indices] += 1
                self.on_3b[score_3rd_indices] = False

            # 2nd base runner scores
            runner_on_2nd_mask = self.on_2b[t_indices]
            if np.any(runner_on_2nd_mask):
                score_2nd_indices = t_indices[runner_on_2nd_mask]
                self.scores[score_2nd_indices] += 1
                self.on_2b[score_2nd_indices] = False

            # 1st base runner scores
            runner_on_1st_mask = self.on_1b[t_indices]
            if np.any(runner_on_1st_mask):
                score_1st_indices = t_indices[runner_on_1st_mask]
                self.scores[score_1st_indices] += 1
                self.on_1b[score_1st_indices] = False

            # Batter to 3rd
            self.on_3b[t_indices] = True

            # 6: Homerun
            hr_mask = outcomes == 6
            hr_indices = indices[hr_mask]

            # All runners score plus the batter - clear each base only if occupied
            # 3rd base runner scores
            runner_on_3rd_mask = self.on_3b[hr_indices]
            if np.any(runner_on_3rd_mask):
                score_3rd_indices = hr_indices[runner_on_3rd_mask]
                self.scores[score_3rd_indices] += 1
                self.on_3b[score_3rd_indices] = False

            # 2nd base runner scores
            runner_on_2nd_mask = self.on_2b[hr_indices]
            if np.any(runner_on_2nd_mask):
                score_2nd_indices = hr_indices[runner_on_2nd_mask]
                self.scores[score_2nd_indices] += 1
                self.on_2b[score_2nd_indices] = False

            # 1st base runner scores
            runner_on_1st_mask = self.on_1b[hr_indices]
            if np.any(runner_on_1st_mask):
                score_1st_indices = hr_indices[runner_on_1st_mask]
                self.scores[score_1st_indices] += 1
                self.on_1b[score_1st_indices] = False

            # Batter scores (home run)
            self.scores[hr_indices] += 1

            # Advance batter for all active games
            self.batter_up[batting_mask] = (self.batter_up[batting_mask] + 1) % 9

    def get_scores(self):
        return self.scores.tolist()
