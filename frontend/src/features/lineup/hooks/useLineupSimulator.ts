/**
 * useLineupSimulator - Hook for managing lineup simulation state and logic
 * Separates business logic from UI presentation
 */

import { useState, useEffect } from "react";
import { SavedLineup, deleteLineup } from "../services/lineupService";
import {
  useMonteCarloSimulation,
  SimulationConfig,
} from "./useMonteCarloSimulation";
import { SIMULATION_CONFIG, STATUS_MESSAGES, UI_MESSAGES } from "shared";

export function useLineupSimulator(
  savedLineups: SavedLineup[],
  onLineupDeleted?: () => void
) {
  const [selectedLineupIds, setSelectedLineupIds] = useState<number[]>([]);
  const [expandedLineupIds, setExpandedLineupIds] = useState<number[]>([]);
  const [includeWobaBaseline, setIncludeWobaBaseline] = useState(false);
  const [numGames, setNumGames] = useState<number>(SIMULATION_CONFIG.DEFAULT_NUM_GAMES);
  const [statusMessage, setStatusMessage] = useState("");

  const {
    results,
    simulating,
    simulationError,
    setSimulationError,
    runSimulations,
    clearResults,
  } = useMonteCarloSimulation();

  // Cycle through status messages while simulating
  useEffect(() => {
    if (!simulating) {
      setStatusMessage("");
      return;
    }

    let currentIndex = 0;
    const interval = setInterval(() => {
      setStatusMessage(STATUS_MESSAGES[currentIndex]);
      currentIndex = (currentIndex + 1) % STATUS_MESSAGES.length;
    }, SIMULATION_CONFIG.STATUS_MESSAGE_INTERVAL);

    return () => clearInterval(interval);
  }, [simulating]);

  const handleToggleLineup = (lineupId: number) => {
    setSelectedLineupIds((prev) => {
      if (prev.includes(lineupId)) {
        return prev.filter((id) => id !== lineupId);
      } else {
        return [...prev, lineupId];
      }
    });
  };

  const toggleExpandLineup = (lineupId: number) => {
    setExpandedLineupIds((prev) =>
      prev.includes(lineupId)
        ? prev.filter((id) => id !== lineupId)
        : [...prev, lineupId]
    );
  };

  const handleClearResults = () => {
    clearResults();
  };

  const handleRunSimulation = async () => {
    if (selectedLineupIds.length === 0) return;

    const configs: SimulationConfig[] = [];

    // Add selected lineups
    selectedLineupIds.forEach((id) => {
      const lineup = savedLineups.find((l) => l.id === id);
      if (lineup) {
        const playerIds = lineup.players
          .sort((a, b) => a.batting_order - b.batting_order)
          .map((p) => p.player_id);

        if (playerIds.length === SIMULATION_CONFIG.LINEUP_SIZE) {
          configs.push({
            id: lineup.id,
            name: lineup.name,
            playerIds: playerIds,
            isBaseline: false,
          });
        }
      }
    });

    if (configs.length === 0) {
      setSimulationError(`No valid lineups selected (must have ${SIMULATION_CONFIG.LINEUP_SIZE} players).`);
      return;
    }

    // Add baseline if requested
    if (includeWobaBaseline && configs.length > 0) {
      // Generate a baseline for each unique set of players found in the selected lineups
      const processedPlayerSets = new Set<string>();
      // Capture the current length so we don't iterate over newly added baselines
      const currentConfigsCount = configs.length;

      for (let i = 0; i < currentConfigsCount; i++) {
        const config = configs[i];
        // Create a unique key for the set of players (independent of batting order)
        const playerSetKey = [...config.playerIds]
          .sort((a, b) => a - b)
          .join(",");

        if (!processedPlayerSets.has(playerSetKey)) {
          processedPlayerSets.add(playerSetKey);
          configs.push({
            id: `baseline-${config.id}`,
            name: `wOBA Baseline (${config.name})`,
            playerIds: config.playerIds,
            isBaseline: true,
          });
        }
      }
    }

    await runSimulations(configs, numGames);
  };

  const handleDeleteLineup = async (lineupId: number, e?: React.MouseEvent) => {
    e?.stopPropagation();
    if (!window.confirm(UI_MESSAGES.DELETE_CONFIRMATION)) return;

    try {
      await deleteLineup(lineupId);
      // Clear selection if deleted lineup was selected
      setSelectedLineupIds((prev) => prev.filter((id) => id !== lineupId));
      // Clear expanded state for deleted lineup
      setExpandedLineupIds((prev) => prev.filter((id) => id !== lineupId));
      // Trigger parent component to refresh the lineup list
      onLineupDeleted?.();
    } catch (err: any) {
      setSimulationError?.(String(err) ?? "Failed to delete lineup");
    }
  };

  return {
    // State
    selectedLineupIds,
    expandedLineupIds,
    includeWobaBaseline,
    numGames,
    statusMessage,
    results,
    simulating,
    simulationError,

    // State setters
    setIncludeWobaBaseline,
    setNumGames,

    // Handlers
    handleToggleLineup,
    toggleExpandLineup,
    handleRunSimulation,
    handleDeleteLineup,
    handleClearResults,
  };
}
