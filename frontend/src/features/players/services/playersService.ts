import { apiRequest } from "@/shared/api";


/**
 * Handles API calls for players.
 */
export const playersService = {
  async fetchAll() {
    return apiRequest("/players");
  },
};