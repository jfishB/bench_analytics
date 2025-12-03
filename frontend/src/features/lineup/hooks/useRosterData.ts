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

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const raw = await lineupService.fetchPlayers(teamId);
      setPlayers(raw);
      // Detect team id if available from player data
      if (raw.length > 0) {
        const first = raw[0];
        // Handle team as string or number
        if (first.team) {
          const parsedTeamId =
            typeof first.team === "number"
              ? first.team
              : parseInt(String(first.team), 10);
          if (!isNaN(parsedTeamId) && parsedTeamId > 0) {
            setTeamId(parsedTeamId);
          } else {
            // Fallback to default team 1 if we have players
            setTeamId(1);
          }
        } else {
          // Fallback to default team 1 if team field is missing
          setTeamId(1);
        }
      }
    } catch (err: any) {
      setError(err?.message ?? String(err));
    } finally {
      setLoading(false);
    }
  }, [teamId]);

  useEffect(() => {
    fetchPlayers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array - teamId is auto-detected from fetched data

  return {
    loading,
    players,
    error,
    setError,
    teamId,
    refreshPlayers: fetchPlayers,
  };
}
