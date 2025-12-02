/**
 * Custom hook for managing roster data fetching and state.
 * Handles loading players from the API and detecting team ID.
 */

import { useCallback, useEffect, useState } from "react";
import { Player } from "../../../shared/types";
import * as lineupService from "../services/lineupService";

export function useRosterData() {
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<Player[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [teamId, setTeamId] = useState<number | undefined>(undefined);
  const [loadingSamplePlayers, setLoadingSamplePlayers] = useState(false);

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const raw = await lineupService.fetchPlayers(teamId);
      setPlayers(raw);
      // Detect team id if available
      if (raw.length > 0) {
        const first = raw[0];
        if (first.team && typeof first.team === "string") {
          const parsedTeamId = parseInt(first.team, 10);
          if (!isNaN(parsedTeamId)) setTeamId(parsedTeamId);
        }
      }
    } catch (err: any) {
      setError(err?.message ?? String(err));
    } finally {
      setLoading(false);
    }
  }, [teamId]);

  // Load sample players from CSV
  const loadSamplePlayers = useCallback(async () => {
    setLoadingSamplePlayers(true);
    setError(null);
    try {
      const result = await lineupService.loadSamplePlayers();
      if (result.success || result.already_loaded) {
        // Refresh the players list
        await fetchPlayers();
      }
      return result;
    } catch (err: any) {
      setError(err?.message ?? String(err));
      throw err;
    } finally {
      setLoadingSamplePlayers(false);
    }
  }, [fetchPlayers]);

  useEffect(() => {
    fetchPlayers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array - teamId is auto-detected from fetched data, not a trigger for refetch

  return {
    loading,
    players,
    error,
    setError,
    teamId,
    loadSamplePlayers,
    loadingSamplePlayers,
    refreshPlayers: fetchPlayers,
  };
}
