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
      throw new Error("Failed to fetch players");
    }
    
    return response.json();
  },
};