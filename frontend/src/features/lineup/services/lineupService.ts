/**
 * Service layer for lineup-related API calls.
 * Centralizes all HTTP requests for better testability and maintainability.
 */

import { Player } from "../../../shared/types";

const API_BASE =
  process.env.REACT_APP_API_BASE || "http://localhost:8000/api/v1";
const ROSTER_BASE = `${API_BASE}/roster`;
const LINEUPS_BASE = `${API_BASE}/lineups`;

// Type definitions for API responses
export interface SavedLineup {
  id: number;
  team_id: number;
  name: string;
  players: Array<{
    player_id: number;
    player_name: string;
    position: string;
    batting_order: number;
  }>;
  created_by: number;
  created_at: string;
}

export interface GeneratedLineup {
  team_id: number;
  players: Array<{
    player_id: number;
    player_name: string;
    position: string;
    batting_order: number;
  }>;
}

export interface SaveLineupPayload {
  team_id: number;
  name: string;
  players: Array<{
    player_id: number;
    position: string;
    batting_order: number;
  }>;
}

/**
 * Fetch all players for a team from the roster.
 */
export async function fetchPlayers(teamId?: number): Promise<Player[]> {
  const res = await fetch(`${ROSTER_BASE}/players/`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  const playersArray = Array.isArray(data) ? data : data.players || data.results || [];
  
  return playersArray.map((p: any) => ({
    id: p.id,
    name: p.name,
    position: p.position,
    team: String(p.team ?? teamId ?? ""),
    avg: p.avg,
    obp: p.obp,
    ops: p.ops,
    batting_order: p.batting_order,
    pa: p.pa,
    on_base_percent: p.on_base_percent,
    hit: p.hit,
    walk: p.walk,
    xwoba: p.xwoba,
    bb_percent: p.bb_percent,
    k_percent: p.k_percent,
    barrel_batted_rate: p.barrel_batted_rate,
  }));
}

/**
 * Fetch all saved lineups from the database.
 */
export async function fetchSavedLineups(): Promise<SavedLineup[]> {
  const res = await fetch(`${LINEUPS_BASE}/saved/`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) ? data : data.results || [];
}

/**
 * Save a lineup to the database (manual or sabermetrics mode).
 */
export async function saveLineup(
  payload: SaveLineupPayload
): Promise<SavedLineup> {
  const res = await fetch(`${LINEUPS_BASE}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errorText}`);
  }
  
  return await res.json();
}

/**
 * Generate a lineup using the backend algorithm (algorithm-only mode).
 * Does not save to database - returns suggested lineup only.
 */
export async function generateLineup(
  teamId: number
): Promise<GeneratedLineup> {
  const payload = { team_id: teamId };
  const res = await fetch(`${LINEUPS_BASE}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}
