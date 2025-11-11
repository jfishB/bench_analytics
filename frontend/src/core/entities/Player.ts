/**
 * Represents a baseball/softball player.
 * 
 * - `id`: Unique player identifier
 * - `name`: Player's full name
 * - `position`: Player's field position
 * - `battingAverage`: Player's batting average
 * - `hits`: Total hits recorded
 * - `atBats`: Total at-bats
 */
export interface Player {
  id: string;
  name: string;
  position: string;
  battingAverage: number;
  hits: number;
  atBats: number;
}
