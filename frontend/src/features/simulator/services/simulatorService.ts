/**
 * Service for interacting with the Monte Carlo baseball simulator API
 */

import { SimulationRequest, SimulationResult } from '../types';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api/v1';
const SIMULATOR_BASE = `${API_BASE}/simulator`;

/**
 * Mock simulation data for development/testing
 */
const generateMockSimulation = (playerIds: number[], numGames: number): SimulationResult => {
  // Generate realistic-looking score distribution
  const distribution: Record<string, number> = {};
  const scores: number[] = [];
  
  // Generate scores with a normal-ish distribution around 3-4 runs
  for (let i = 0; i < numGames; i++) {
    // Weighted random score (0-15 runs, most common around 3-4)
    const random = Math.random();
    let score: number;
    if (random < 0.09) score = 0;
    else if (random < 0.23) score = 1;
    else if (random < 0.39) score = 2;
    else if (random < 0.54) score = 3;
    else if (random < 0.67) score = 4;
    else if (random < 0.77) score = 5;
    else if (random < 0.85) score = 6;
    else if (random < 0.91) score = 7;
    else if (random < 0.95) score = 8;
    else if (random < 0.97) score = 9;
    else if (random < 0.985) score = 10;
    else if (random < 0.993) score = 11;
    else if (random < 0.997) score = 12;
    else score = Math.floor(Math.random() * 8) + 13; // 13-20
    
    scores.push(score);
    distribution[score] = (distribution[score] || 0) + 1;
  }
  
  // Calculate statistics
  const sortedScores = scores.sort((a, b) => a - b);
  const avg = scores.reduce((sum, s) => sum + s, 0) / scores.length;
  const median = sortedScores[Math.floor(sortedScores.length / 2)];
  const variance = scores.reduce((sum, s) => sum + Math.pow(s - avg, 2), 0) / scores.length;
  const stdDev = Math.sqrt(variance);
  
  return {
    lineup: playerIds.map(id => `Player ${id}`),
    num_games: numGames,
    avg_score: Number(avg.toFixed(2)),
    median_score: median,
    std_dev: Number(stdDev.toFixed(2)),
    min_score: Math.min(...scores),
    max_score: Math.max(...scores),
    score_distribution: distribution,
  };
};

export const simulatorService = {
  /**
   * Run simulation with player IDs
   */
  async simulateByPlayerIds(request: SimulationRequest): Promise<SimulationResult> {
    try {
      const response = await fetch(`${SIMULATOR_BASE}/simulate-by-ids/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // TODO: Add auth token when backend is ready
          // 'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.warn('Backend unavailable, using mock data:', error);
      // Return mock data for development
      return generateMockSimulation(request.player_ids, request.num_games);
    }
  },

  /**
   * Run simulation with player names
   */
  async simulateByPlayerNames(playerNames: string[], numGames: number): Promise<SimulationResult> {
    try {
      const response = await fetch(`${SIMULATOR_BASE}/simulate-by-names/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_names: playerNames, num_games: numGames }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.warn('Backend unavailable, using mock data:', error);
      // Generate mock IDs for player names
      const mockIds = playerNames.map((_, idx) => idx + 1);
      const result = generateMockSimulation(mockIds, numGames);
      result.lineup = playerNames;
      return result;
    }
  },

  /**
   * Run simulation for a team
   */
  async simulateByTeam(teamId: number, numGames: number): Promise<SimulationResult> {
    try {
      const response = await fetch(`${SIMULATOR_BASE}/simulate-by-team/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ team_id: teamId, num_games: numGames }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.warn('Backend unavailable, using mock data:', error);
      const mockIds = Array.from({ length: 9 }, (_, i) => i + 1);
      return generateMockSimulation(mockIds, numGames);
    }
  },
};
