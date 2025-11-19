/**
 * Service layer for lineup-related API calls.
 * Centralizes all HTTP requests for better testability and maintainability.
 */

import { Player } from "../../../shared/types";

const API_BASE =
  process.env.REACT_APP_API_BASE || "http://localhost:8000/api/v1";
const ROSTER_BASE = `${API_BASE}/roster`;
const LINEUPS_BASE = `${API_BASE}/lineups`;
const AUTH_BASE = `${API_BASE}/auth`;

/**
 * Helper function to refresh the access token using the refresh token.
 */
async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = localStorage.getItem("refresh");
  if (!refreshToken) {
    return false;
  }

  try {
    const res = await fetch(`${AUTH_BASE}/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!res.ok) {
      return false;
    }

    const data = await res.json();
    localStorage.setItem("access", data.access);
    return true;
  } catch (err) {
    console.error("Token refresh failed:", err);
    return false;
  }
}

// Type definitions for API responses
export interface SavedLineup {
  id: number;
  team_id: number;
  name: string;
  players: Array<{
    player_id: number;
    player_name: string;
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
    batting_order: number;
  }>;
}

export interface SaveLineupPayload {
  team_id: number;
  name: string;
  players: Array<{
    player_id: number;
    // position removed from backend
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
  const playersArray = Array.isArray(data)
    ? data
    : data.players || data.results || [];

  return playersArray.map((p: any) => ({
    id: p.id,
    name: p.name,
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
  teamId: number,
  playerIds?: number[]
): Promise<GeneratedLineup> {
  const payload: any = { team_id: teamId };
  if (playerIds && playerIds.length > 0) {
    payload.players = playerIds.map((id) => ({ player_id: id }));
  }

  const res = await fetch(`${LINEUPS_BASE}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// Type definitions for Monte Carlo simulation
export interface SimulationRequest {
  player_ids: number[];
  num_games?: number;
}

export interface SimulationResult {
  lineup: string[];
  num_games: number;
  avg_score: number;
  median_score: number;
  std_dev: number;
  min_score: number;
  max_score: number;
  score_distribution: { [key: string]: number };
}

/**
 * Run Monte Carlo simulation on a lineup.
 * Takes 9 player IDs in batting order and simulates N games.
 * Automatically refreshes JWT token and retries if authentication fails.
 */
export async function runSimulation(
  playerIds: number[],
  numGames: number = 10000
): Promise<SimulationResult> {
  const SIMULATOR_BASE = `${API_BASE}/simulator`;

  const payload: SimulationRequest = {
    player_ids: playerIds,
    num_games: numGames,
  };

  // First attempt
  let res = await fetch(`${SIMULATOR_BASE}/simulate-by-ids/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("access")}`,
    },
    body: JSON.stringify(payload),
  });

  // If 401, try to refresh token and retry
  if (res.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry with new token
      res = await fetch(`${SIMULATOR_BASE}/simulate-by-ids/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access")}`,
        },
        body: JSON.stringify(payload),
      });
    }
  }

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Simulation failed (HTTP ${res.status}): ${errorText}`);
  }

  return await res.json();
}
