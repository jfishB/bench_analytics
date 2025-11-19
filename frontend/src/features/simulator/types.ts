/**
 * Type definitions for Monte Carlo baseball simulator
 */

export interface SimulationResult {
  lineup: string[];
  num_games: number;
  avg_score: number;
  median_score: number;
  std_dev: number;
  min_score: number;
  max_score: number;
  score_distribution: Record<string, number>;
}

export interface SimulationRequest {
  player_ids: number[];
  num_games: number;
}

export interface Player {
  id: number;
  name: string;
  first_name?: string;
  last_name?: string;
  plate_appearances?: number;
  hits?: number;
  doubles?: number;
  triples?: number;
  home_runs?: number;
  strikeouts?: number;
  walks?: number;
}
