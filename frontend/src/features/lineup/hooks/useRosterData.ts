/**
 * Custom hook for managing roster data fetching and state.
 * Handles loading players from the API and detecting team ID.
 */

import { useEffect, useState } from "react";
import { Player } from "../../../shared/types";
import * as lineupService from "../services/lineupService";

export function useRosterData() {
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<Player[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [teamId, setTeamId] = useState<number | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;

    async function loadPlayers() {
      setLoading(true);
      setError(null);
      try {
        const raw = await lineupService.fetchPlayers(teamId);
        if (!cancelled) {
          setPlayers(raw);
          // Detect team id if available
          if (raw.length > 0) {
            const first = raw[0];
            if (first.team && typeof first.team === "string") {
              const parsedTeamId = parseInt(first.team, 10);
              if (!isNaN(parsedTeamId)) setTeamId(parsedTeamId);
            }
          }
        }
      } catch (err: any) {
        if (!cancelled) setError(err?.message ?? String(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadPlayers();

    return () => {
      cancelled = true;
    };
  }, []); // Empty dependency array - teamId is auto-detected from fetched data

  return {
    loading,
    players,
    error,
    setError,
    teamId,
  };
}

