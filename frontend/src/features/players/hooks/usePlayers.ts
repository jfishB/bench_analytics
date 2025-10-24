import { useEffect, useState } from "react";
import { playersService } from "../services/playersService";

/**
 * Custom hook to fetch players and manage loading state.
 */
export function usePlayers() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    playersService
      .fetchAll()
      .then(setPlayers)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  return { players, loading, error };
}
