/**
 * Custom hook for managing saved lineups fetching and state.
 * Handles loading all saved lineups from the database.
 */

import { useState } from "react";
import * as lineupService from "../services/lineupService";

export function useSavedLineups() {
  const [savedLineups, setSavedLineups] = useState<lineupService.SavedLineup[]>([]);
  const [loadingLineups, setLoadingLineups] = useState(false);

  const fetchSavedLineups = async () => {
    setLoadingLineups(true);
    try {
      const data = await lineupService.fetchSavedLineups();
      setSavedLineups(data);
    } catch (err: any) {
      console.error("Failed to fetch lineups:", err);
    } finally {
      setLoadingLineups(false);
    }
  };

  return {
    savedLineups,
    loadingLineups,
    fetchSavedLineups,
  };
}

