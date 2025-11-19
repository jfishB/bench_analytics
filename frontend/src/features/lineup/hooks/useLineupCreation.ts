/**
 * Custom hook for managing lineup creation workflow.
 * Handles the overall lineup creation state and mode switching.
 */

import { useState } from "react";
import { Player } from "../../../shared/types";

export function useLineupCreation() {
  const [lineupCreated, setLineupCreated] = useState<boolean>(false);
  const [lineupMode, setLineupMode] = useState<"manual" | "sabermetrics">("manual");
  const [lineupPlayers, setLineupPlayers] = useState<Player[]>([]);
  const [selected, setSelected] = useState<Player | null>(null);

  const createLineup = (players: Player[]) => {
    const selectedPlayers = players.map((p, index) => ({
      ...p,
      batting_order: index + 1,
    }));
    setLineupPlayers(selectedPlayers);
    setLineupCreated(true);
    return selectedPlayers;
  };

  const resetLineup = () => {
    setLineupCreated(false);
    setLineupPlayers([]);
  };

  return {
    lineupCreated,
    setLineupCreated,
    lineupMode,
    setLineupMode,
    lineupPlayers,
    setLineupPlayers,
    selected,
    setSelected,
    createLineup,
    resetLineup,
  };
}

