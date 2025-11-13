/**
 * Centralized TypeScript interfaces and type definitions shared across the app.
 */

export type Player = {
  id: number;
  name: string;
  team?: string;
  position: string;
  avg?: number;
  obp?: number;
  ops?: number;
  batting_order?: number;
}
