/**
 * shared/types.ts
 * Shared Typescript interfaces and types.
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
