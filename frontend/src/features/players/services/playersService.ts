/**
 * playersService
 *
 * Encapsulates all API calls related to players.
 * - Makes it easy to swap or mock API requests for testing.
 */

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000/api/v1";

export const playersService = {
  /**
   * Fetches all players from the backend.
   * @returns Promise resolving to an array of player objects
   */
  async fetchAll() {
    const response = await fetch(`${API_BASE}/players`);
    
    if (!response.ok) {
      const status = response.status;
      if (status === 404) {
        throw new Error("Players endpoint not found");
      } else if (status >= 500) {
        throw new Error("Server error while fetching players");
      } else if (status === 401 || status === 403) {
        throw new Error("Unauthorized to fetch players");
      }
      throw new Error(`Failed to fetch players (status: ${status})`);
    }
    
    return response.json();
  },
};