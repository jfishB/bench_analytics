/**
 * Hook for managing simulation state and execution
 */

import { useState } from 'react';
import { SimulationResult } from '../types';
import { simulatorService } from '../services/simulatorService';

export const useSimulation = () => {
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runSimulationByIds = async (playerIds: number[], numGames: number = 10000) => {
    if (playerIds.length !== 9) {
      setError('Lineup must have exactly 9 players');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await simulatorService.simulateByPlayerIds({
        player_ids: playerIds,
        num_games: numGames,
      });
      setSimulationResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const runSimulationByNames = async (playerNames: string[], numGames: number = 10000) => {
    if (playerNames.length !== 9) {
      setError('Lineup must have exactly 9 players');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await simulatorService.simulateByPlayerNames(playerNames, numGames);
      setSimulationResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setSimulationResult(null);
    setError(null);
  };

  return {
    simulationResult,
    isLoading,
    error,
    runSimulationByIds,
    runSimulationByNames,
    clearResults,
  };
};
