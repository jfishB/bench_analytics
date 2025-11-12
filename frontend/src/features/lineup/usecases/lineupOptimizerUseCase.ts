import { Player } from "../../../shared/types";

export function generateLineup(players: Player[]): Player[] {
  // Sort by OPS descending
  const sortedByOPS = [...players].sort((a, b) => (b.ops ?? 0) - (a.ops ?? 0));

  // Simple heuristic: pick top OBP and AVG
  const optimizedOrder = [
    sortedByOPS.find((p) => (p.obp ?? 0) > 0.35) || sortedByOPS[0],
    sortedByOPS.find((p) => (p.avg ?? 0) > 0.3 && (p.obp ?? 0) > 0.35) || sortedByOPS[1],
    sortedByOPS[0],
    sortedByOPS[1],
    sortedByOPS[2],
    ...sortedByOPS.slice(3),
  ].filter(Boolean).slice(0, 9);

  return optimizedOrder;
}
