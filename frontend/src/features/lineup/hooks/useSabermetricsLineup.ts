/**
 * Custom hook for managing sabermetrics lineup generation.
 * Handles algorithm-based lineup creation and save functionality.
 */

import { useState } from "react";
import { Player } from "../../../shared/types";
import * as lineupService from "../services/lineupService";

export function useSabermetricsLineup(
  teamId: number | undefined,
  players: Player[],
  onSaveSuccess?: () => void
) {
  const [generatedLineup, setGeneratedLineup] = useState<Player[]>([]);
  const [generating, setGenerating] = useState(false);
  const [sabermetricsLineupName, setSabermetricsLineupName] = useState<string>("");
  const [sabermetricsSaveStatus, setSabermetricsSaveStatus] = useState<
    "idle" | "saving" | "saved"
  >("idle");

  const generateLineup = async (selectedIds?: number[]) => {
    if (!teamId) {
      throw new Error("Team ID is required");
    }

    setGenerating(true);
    try {
      const data = await lineupService.generateLineup(teamId, selectedIds);
      const ordered = (data.players || []).map((p: any) => {
        const full = players.find((r) => r.id === p.player_id) || {
          id: p.player_id,
          name: p.player_name ?? "Unknown",
          team: String(p.team ?? teamId),
        };
        return {
          ...full,
          batting_order: p.batting_order,
        };
      });
      setGeneratedLineup(ordered);
    } catch (err: any) {
      console.error("Generation failed:", err);
      throw err;
    } finally {
      setGenerating(false);
    }
  };

  const saveLineup = async () => {
    if (!teamId) {
      throw new Error("Team ID is required");
    }

    setSabermetricsSaveStatus("saving");
    try {
      const payload: lineupService.SaveLineupPayload = {
        team_id: teamId,
        name: sabermetricsLineupName,
        players: generatedLineup.map((p) => ({
          player_id: p.id,
            // position removed from model; backend will no longer expect it
          batting_order: p.batting_order!,
        })),
      };

      await lineupService.saveLineup(payload);

      setSabermetricsSaveStatus("saved");
      onSaveSuccess?.();

      setTimeout(() => {
        setSabermetricsSaveStatus("idle");
        setSabermetricsLineupName("");
      }, 1000);
    } catch (err: any) {
      console.error("Failed to save lineup:", err);
      setSabermetricsSaveStatus("idle");
      throw err;
    }
  };

  const clearGeneratedLineup = () => {
      setGeneratedLineup([]);
      setSabermetricsLineupName("");
    };

  return {
    generatedLineup,
    generating,
    sabermetricsLineupName,
    setSabermetricsLineupName,
    sabermetricsSaveStatus,
    generateLineup,
    saveLineup,
    clearGeneratedLineup,
  };
}

