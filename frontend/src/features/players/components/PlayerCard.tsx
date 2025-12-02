import React from "react";
import PlayerCardUI from "ui/components/player-card";
import type { Player } from "shared";

interface PlayerCardProps {
  player: Pick<Player, "name" | "team">;
}

/**
 * PlayerCard wrapper (Feature layer)
 *
 * - Wraps the UI primitive `PlayerCard` with data from the Player type.
 * - Maps `player.team` → `teamName`.
 * - Adds spacing or any feature-specific props here.
 */
export function PlayerCard({ player }: PlayerCardProps) {
  return (
    <PlayerCardUI name={player.name} teamName={player.team} className="mb-3" />
  );
}
