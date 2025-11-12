import { Player } from "../../../shared/types";

function normalizePlayers(data: any[]): Player[] {
  return data.map((p) => ({
    id: p.id,
    name: p.name,
    position: p.position,
    team: p.team ?? undefined,
    avg: p.avg ?? undefined,
    obp: p.obp ?? undefined,
    ops: p.ops ?? undefined,
    batting_order: p.batting_order ?? undefined,
  }));
}

export async function fetchRoster(): Promise<Player[]> {
  const res = await fetch("/api/roster");
  if (!res.ok) throw new Error("Failed to fetch roster");
  const data = await res.json();
  return Array.isArray(data) ? normalizePlayers(data) : [];
}

export async function fetchLineup(): Promise<Player[]> {
  const res = await fetch("/api/lineup");
  if (!res.ok) throw new Error("Failed to fetch lineup");
  const data = await res.json();
  return Array.isArray(data) ? normalizePlayers(data) : [];
}

export async function generateLineupBackend(): Promise<Player[]> {
  const res = await fetch("/api/lineup/generate", { method: "POST" });
  if (!res.ok) throw new Error("Failed to generate lineup");
  const data = await res.json();
  return Array.isArray(data) ? normalizePlayers(data) : [];
}

export async function saveLineup(name: string, lineup: Player[]): Promise<void> {
  const res = await fetch("/api/lineup/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, lineup }),
  });
  if (!res.ok) throw new Error("Failed to save lineup");
}
