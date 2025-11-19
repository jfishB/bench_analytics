/**
 * Custom hook for managing manual lineup creation state.
 * Handles batting order, drag-and-drop, and save functionality.
 */

import { useState } from "react";
import { DragEndEvent } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import { Player } from "../../../shared/types";
import * as lineupService from "../services/lineupService";

export function useManualLineup(
  teamId: number | undefined,
  onSaveSuccess?: () => void
) {
  const [battingOrderLineup, setBattingOrderLineup] = useState<Player[]>([]);
  const [manualLineupName, setManualLineupName] = useState<string>("");
  const [manualSaveStatus, setManualSaveStatus] = useState<
    "idle" | "saving" | "saved"
  >("idle");

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setBattingOrderLineup((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);

        const newOrder = arrayMove(items, oldIndex, newIndex);
        return newOrder.map((player: Player, index: number) => ({
          ...player,
          batting_order: index + 1,
        }));
      });
    }
  };

  const saveLineup = async () => {
    if (!teamId) {
      throw new Error("Team ID is required");
    }

    setManualSaveStatus("saving");
    try {
      const payload: lineupService.SaveLineupPayload = {
        team_id: teamId,
        name: manualLineupName,
        players: battingOrderLineup.map((p) => ({
          player_id: p.id,
          batting_order: p.batting_order!,
        })),
      };

      await lineupService.saveLineup(payload);

      setManualSaveStatus("saved");
      onSaveSuccess?.();

      setTimeout(() => {
        setManualSaveStatus("idle");
        setManualLineupName("");
      }, 1000);
    } catch (err: any) {
      console.error("Failed to save lineup:", err);
      setManualSaveStatus("idle");
      throw err;
    }
  };

  return {
    battingOrderLineup,
    setBattingOrderLineup,
    manualLineupName,
    setManualLineupName,
    manualSaveStatus,
    handleDragEnd,
    saveLineup,
  };
}

