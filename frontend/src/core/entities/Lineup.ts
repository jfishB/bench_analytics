import { Player } from "./Player";

/**
 * Represents a team lineup.
 * 
 * - `teamId`: Unique identifier for the team
 * - `players`: Array of Player objects in the lineup
 */
export interface Lineup {
  teamId: string;
  players: Player[];
}