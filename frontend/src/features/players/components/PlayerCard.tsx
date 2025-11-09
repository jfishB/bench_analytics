import React from "react";
import { Card } from "../../../ui/components/card";

import type { Player } from "../../../shared/types";
interface PlayerCardProps {
  player: Pick<Player, "name" | "team" | "position">;
}

/**
 * Displays basic player info.
 */
export function PlayerCard({ player }: PlayerCardProps) {
  return (
    <Card className="mb-3">
      <h3 className="text-lg font-semibold">{player.name}</h3>
      <p>{player.team}</p>
      <p className="text-sm text-gray-500">{player.position}</p>
    </Card>
  );
}
