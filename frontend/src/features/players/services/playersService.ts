import { apiRequest } from "@/services/api";


/**
 * Handles API calls for players.
 */
export const playersService = {
  async fetchAll() {
    return apiRequest("/players");
  },
};