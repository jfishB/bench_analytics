import React from "react";
import PlayerList from "../../../ui/components/player-list";
import type { Player } from "../../../shared/types"; // player type defined in shared/types

interface PlayersOrderedListProps {
  players: Array<
    Partial<Player> & { batting_order?: number | null; isSelected?: boolean }
  >;
  className?: string;
  onItemClick?: (player: Player) => void;
  badgeClassName?: string;
  onSelectionToggle?: (player: Player) => void;
  showCheckboxes?: boolean;
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
  badgeClassName = "bg-primary text-white dark:bg-primary",
  onSelectionToggle,
  showCheckboxes = false,
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

  // Map to the UI primitive's expected structure. Keep payload as Partial<Player>.
  const items = sorted.map((p) => ({
    id: p.id !== undefined && p.id !== null ? String(p.id) : undefined,
    name: p.name ?? "Unnamed",
    battingOrder: p.batting_order ?? null,
    payload: p,
    isSelected: p.isSelected || false,
  }));

  // Type guard: ensure a Partial<Player> is a complete Player before calling the consumer
  function isCompletePlayer(p: Partial<Player> | undefined): p is Player {
    return (
      !!p &&
      typeof p.id !== "undefined" &&
      typeof p.name === "string" &&
      true
    );
  }

  return (
    <PlayerList
      items={items}
      className={className}
      onItemClick={(it) => {
        const payload = it.payload as Partial<Player> | undefined;
        if (!payload) return;
        if (onItemClick && isCompletePlayer(payload)) {
          onItemClick(payload);
        } else {
          console.warn(
            "PlayersOrderedList: onItemClick skipped due to incomplete player data",
            payload
          );
        }
      }}
      onSelectionToggle={
        onSelectionToggle
          ? (it) => {
              const payload = it.payload as Partial<Player> | undefined;
              if (!payload) return;
              if (isCompletePlayer(payload)) {
                onSelectionToggle(payload);
              }
            }
          : undefined
      }
      showCheckboxes={showCheckboxes}
      badgeClassName={badgeClassName}
    />
  );
}

export default PlayersOrderedList;
