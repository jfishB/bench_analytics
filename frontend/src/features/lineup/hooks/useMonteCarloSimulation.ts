/**
 * Custom hook for managing Monte Carlo simulation state.
 * Handles running simulations on saved lineups and managing results.
 * Compares user lineup against wOBA-sorted baseline.
 */

import { useState } from "react";
import * as lineupService from "../services/lineupService";

export interface ComparisonResult {
  userLineup: lineupService.SimulationResult;
  baselineLineup: lineupService.SimulationResult;
  winner: "user" | "baseline" | "tie";
  difference: number;
}

export function useMonteCarloSimulation() {
  const [comparisonResult, setComparisonResult] =
    useState<ComparisonResult | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  const runSimulation = async (
    playerIds: number[],
    numGames: number = 10000
  ) => {
    setSimulating(true);
    setSimulationError(null);

    try {
      // Run simulation on user's selected lineup
      const userResult = await lineupService.runSimulation(playerIds, numGames);

      // Sort same players by wOBA and run baseline simulation
      const wobaOrderedIds = await lineupService.sortPlayersByWOBA(playerIds);
      const baselineResult = await lineupService.runSimulation(
        wobaOrderedIds,
        numGames
      );

      // Determine winner
      const difference = userResult.avg_score - baselineResult.avg_score;
      let winner: "user" | "baseline" | "tie";
      if (Math.abs(difference) < 0.01) {
        winner = "tie";
      } else if (difference > 0) {
        winner = "user";
      } else {
        winner = "baseline";
      }

      setComparisonResult({
        userLineup: userResult,
        baselineLineup: baselineResult,
        winner,
        difference,
      });
    } catch (err: any) {
      console.error("Simulation failed:", err);
      setSimulationError(err.message || "Failed to run simulation");
      setComparisonResult(null);
    } finally {
      setSimulating(false);
    }
  };

  const clearResults = () => {
    setComparisonResult(null);
    setSimulationError(null);
  };

  return {
    comparisonResult,
    simulating,
    simulationError,
    runSimulation,
    clearResults,
  };
}
