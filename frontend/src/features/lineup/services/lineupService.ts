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

/**
 * Helper to perform authenticated requests with automatic token refresh.
 */
async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const getHeaders = () => {
    const headers: any = {
      "Content-Type": "application/json",
      ...options.headers,
    };
    const token = localStorage.getItem("access");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  };

  let res = await fetch(url, { ...options, headers: getHeaders() });

  if (res.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      res = await fetch(url, { ...options, headers: getHeaders() });
    } else {
      // Refresh failed - clear tokens so UI can redirect to login
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
    }
  }

  return res;
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
 * Sort a list of player IDs by wOBA (descending) to create a baseline lineup.
 * Calls backend endpoint to sort players by xwoba.
 */
export async function sortPlayersByWOBA(
  playerIds: number[]
): Promise<number[]> {
  const response = await authenticatedFetch(
    `${ROSTER_BASE}/sort-by-woba/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ player_ids: playerIds }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to sort players by wOBA");
  }

  const data = await response.json();
  return data.player_ids;
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
  const res = await authenticatedFetch(`${LINEUPS_BASE}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("Save lineup failed:", res.status, errorText);
    throw new Error(`HTTP ${res.status}: ${errorText}`);
  }

  return await res.json();
}

/**
 * Delete a lineup from the database (manual or sabermetrics mode).
 */
export async function deleteLineup(
  lineupId: number
): Promise<void> {
  const url = `${LINEUPS_BASE}/${lineupId}/`;

  const res = await authenticatedFetch(url, {
    method: "DELETE",
  });

  if (!res.ok) {
    const text = await res.text();
    console.error("Delete failed:", res.status, text);
    throw new Error(`HTTP ${res.status}: ${text}`);
  }

  return;
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
  numGames: number = 20000
): Promise<SimulationResult> {
  const SIMULATOR_BASE = `${API_BASE}/simulator`;

  const payload: SimulationRequest = {
    player_ids: playerIds,
    num_games: numGames,
  };

  const res = await authenticatedFetch(`${SIMULATOR_BASE}/simulate-by-ids/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Simulation failed (HTTP ${res.status}): ${errorText}`);
  }

  return await res.json();
}
