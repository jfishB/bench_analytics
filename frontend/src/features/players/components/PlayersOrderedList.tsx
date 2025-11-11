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
 * Feature component: sorts players by `batting_order` (ascending) and
 * renders the UI primitive `PlayerList`.
 * Ordering is not business logic, just nicer UI.
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
