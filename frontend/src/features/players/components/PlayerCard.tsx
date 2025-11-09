import React from "react";
import PlayerCardUI from "../../../ui/components/player-card";

import type { Player } from "../../../shared/types";

interface PlayerCardProps {
  player: Pick<Player, "name" | "team" | "position">;
}

/**
 * Feature wrapper around the UI primitive `PlayerCard`.
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
