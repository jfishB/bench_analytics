import { apiRequest } from "../../../services/api";

/**
 * playersService
 *
 * Encapsulates all API calls related to players.
 * - Makes it easy to swap or mock API requests for testing.
 */
export const playersService = {
  /**
   * Fetches all players from the backend.
   * @returns Promise resolving to an array of player objects
   */
  async fetchAll() {
    return apiRequest("/players");
  },
};