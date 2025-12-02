/**
 * Custom hook for managing player selection logic.
 * Handles selecting up to 9 players with validation warnings.
 */

import { useState } from "react";
import { Player } from "shared";

export function usePlayerSelection() {
  const [selectedPlayerIds, setSelectedPlayerIds] = useState<Set<number>>(
    new Set()
  );
  const [selectionWarning, setSelectionWarning] = useState<string | null>(null);

  const togglePlayerSelection = (player: Player, onLineupChange?: () => void) => {
    const playerId = player.id;
    setSelectedPlayerIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(playerId)) {
        newSet.delete(playerId);
        setSelectionWarning(null);
        onLineupChange?.();
      } else {
        if (newSet.size >= 9) {
          setSelectionWarning(
            "A maximum of 9 players can be selected for a lineup!"
          );
          setTimeout(() => setSelectionWarning(null), 4000);
          return prev;
        }
        newSet.add(playerId);
        onLineupChange?.();
      }
      return newSet;
    });
  };

  const clearSelection = () => {
    setSelectedPlayerIds(new Set());
    setSelectionWarning(null);
  };

  return {
    selectedPlayerIds,
    selectionWarning,
    setSelectionWarning,
    togglePlayerSelection,
    clearSelection,
  };
}

