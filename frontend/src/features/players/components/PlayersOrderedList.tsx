import React from "react";
import PlayerList from "../../../ui/components/player-list";
import type { Player } from "../../../shared/types"; // player type defined in shared/types

interface PlayersOrderedListProps {
  players: Array<Partial<Player> & { batting_order?: number | null }>;
  className?: string;
  onItemClick?: (player: Player) => void;
  badgeClassName?: string;
}

/**
 * PlayersOrderedList (Feature component)
 *
 * - Sorts the provided players by `batting_order` in ascending order.
 *   - Players without a batting_order are pushed to the end.
 * - Maps the sorted data to the `PlayerList` UI primitive.
 * - Handles missing names by defaulting to `"Unnamed"`.
 * - Purely a UI convenience; does not modify business logic.
 */
export function PlayersOrderedList({
  players,
  className = "",
  onItemClick,
  badgeClassName,
}: PlayersOrderedListProps) {
  // Copy and sort: players with undefined/null batting_order go to the end.
  const sorted = [...players].sort((a, b) => {
    const ao = a.batting_order;
    const bo = b.batting_order;
    if (ao == null && bo == null) return 0;
    if (ao == null) return 1;
    if (bo == null) return -1;
    return ao - bo;
  });

  // Map to the UI primitive's expected structure
  const items = sorted.map((p) => ({
    id: String(p.id),
    name: p.name ?? "Unnamed",
    battingOrder: p.batting_order ?? null,
    payload: p as Player,
  }));

  return (
    <PlayerList
      items={items}
      className={className}
      onItemClick={(it) => onItemClick && onItemClick(it.payload as Player)}
      badgeClassName={badgeClassName}
    />
  );
}

export default PlayersOrderedList;
