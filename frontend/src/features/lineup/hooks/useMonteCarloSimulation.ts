/**
 * Custom hook for managing Monte Carlo simulation state.
 * Handles running simulations on saved lineups and managing results.
 */

import { useState } from "react";
import * as lineupService from "../services/lineupService";

export function useMonteCarloSimulation() {
  const [simulationResult, setSimulationResult] =
    useState<lineupService.SimulationResult | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  const runSimulation = async (
    playerIds: number[],
    numGames: number = 10000
  ) => {
    setSimulating(true);
    setSimulationError(null);

    try {
      const result = await lineupService.runSimulation(playerIds, numGames);
      setSimulationResult(result);
    } catch (err: any) {
      console.error("Simulation failed:", err);
      setSimulationError(err.message || "Failed to run simulation");
      setSimulationResult(null);
    } finally {
      setSimulating(false);
    }
  };

  const clearResults = () => {
    setSimulationResult(null);
    setSimulationError(null);
  };

  return {
    simulationResult,
    simulating,
    simulationError,
    runSimulation,
    clearResults,
  };
}

