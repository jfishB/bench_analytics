/**
 * Centralized TypeScript interfaces and type definitions shared across the app.
 */

export type Player = {
  id: number;
  name: string;
  team?: string;
  avg?: number;
  obp?: number;
  ops?: number;
  batting_order?: number;
  pa?: number;
  on_base_percent?: number;
  hit?: number;
  walk?: number;
  xwoba?: number;
  bb_percent?: number;
  k_percent?: number;
  barrel_batted_rate?: number;
}

