import React from "react";
import PlayerCardUI from "../../../ui/components/player-card";

import type { Player } from "../../../shared/types";

interface PlayerCardProps {
  player: Pick<Player, "name" | "team" | "position">;
}

/**
 * PlayerCard wrapper (Feature layer)
 *
 * - Wraps the UI primitive `PlayerCard` with data from the Player type.
 * - Maps `player.team` → `teamName` and `player.position` → `battingPosition`.
 * - Adds spacing or any feature-specific props here.
 */
export function PlayerCard({ player }: PlayerCardProps) {
  return (
    <PlayerCardUI
      name={player.name}
      teamName={player.team}
      battingPosition={player.position}
      className="mb-3"
    />
  );
}
