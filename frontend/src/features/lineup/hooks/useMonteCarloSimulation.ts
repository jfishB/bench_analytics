/**
 * Custom hook for managing Monte Carlo simulation state.
 * Handles running simulations on saved lineups and managing results.
 * Supports multiple concurrent simulations.
 */

import { useState } from "react";
import * as lineupService from "../services/lineupService";

export interface SimulationConfig {
  id: string | number; // Unique identifier for the lineup (e.g., lineup ID or "baseline")
  name: string;
  playerIds: number[];
  isBaseline?: boolean; // If true, will sort players by wOBA before simulating
}

export interface SimulationResultWithMetadata extends lineupService.SimulationResult {
  id: string | number;
  name: string;
  isBaseline: boolean;
}

export function useMonteCarloSimulation() {
  const [results, setResults] = useState<SimulationResultWithMetadata[]>([]);
  const [simulating, setSimulating] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  const runSimulations = async (
    configs: SimulationConfig[],
    numGames: number = 10000
  ) => {
    setSimulating(true);
    setSimulationError(null);
    setResults([]);

    try {
      const promises = configs.map(async (config) => {
        let playerIdsToSimulate = [...config.playerIds];

        // If baseline, sort by wOBA first
        if (config.isBaseline) {
          playerIdsToSimulate = await lineupService.sortPlayersByWOBA(
            playerIdsToSimulate
          );
        }

        const result = await lineupService.runSimulation(
          playerIdsToSimulate,
          numGames
        );

        return {
          ...result,
          id: config.id,
          name: config.name,
          isBaseline: !!config.isBaseline,
        };
      });

      const simulationResults = await Promise.all(promises);

      // Sort results by average score descending (winner first)
      simulationResults.sort((a, b) => b.avg_score - a.avg_score);

      setResults(simulationResults);
    } catch (err: any) {
      console.error("Simulation failed:", err);
      setSimulationError(err.message || "Failed to run simulation");
      setResults([]);
    } finally {
      setSimulating(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setSimulationError(null);
  };

  return {
    results,
    simulating,
    simulationError,
    setSimulationError,
    runSimulations,
    clearResults,
  };
}
