/**
 * Centralized TypeScript interfaces and type definitions shared across the app.
 */

export type Player = {
  id: string;
  name: string;
  team?: string;
  position: string;
  average?: number;
  obp?: number;
  ops?: number;
  batting_order?: number;
}
