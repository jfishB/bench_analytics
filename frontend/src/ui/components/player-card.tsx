import React from "react";

import { cn } from "../../utils";

interface PlayerCardProps {
  id?: string | number; // optional player ID
  name: string; // player name
  teamName?: string; // optional team name
  battingPosition?: string | number | null; // optional batting position
  className?: string; // additional styling classes
}

/**
 * PlayerCard (UI primitive)
 *
 * Displays a single player's key info:
 * - Prominent player name
 * - Subtle team name
 * - Optional batting position (shows "--" when not provided)
 *
 * Layout is flexible and allows additional meta fields to be added below the main info.
 * Add comments here when additional fields are created.
 */
export function PlayerCard({
  id,
  name,
  teamName,
  battingPosition,
  className = "",
}: PlayerCardProps) {
  return (
    <article
      data-player-id={id}
      className={cn(
        "bg-white shadow-sm border border-gray-100 rounded-lg p-4 w-full max-w-xs",
        className
      )}
    >
      {/* Player name */}
      <header className="mb-2">
        <h3
          className="text-lg font-semibold text-gray-900 truncate"
          title={name}
        >
          {name}
        </h3>
      </header>

      {/* Team and Position Info */}
      <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">Team</span>
          <span className="text-sm font-medium text-gray-800">
            {teamName || "--"}
          </span>
        </div>

        {/* Batting position */}
        <div className="flex flex-col items-end">
          <span className="text-xs text-gray-500">Position</span>
          <span className="text-sm font-medium text-gray-800">
            {battingPosition ?? "--"}
          </span>
        </div>
      </div>

      {/*
        Additional data can be placed here 
        Add markup below to display those extra fields.
      */}
      <div className="meta text-xs text-gray-600">
        {/* PLACEHOLDER FOR ADDITIONAL FIELDS */}
      </div>
    </article>
  );
}
export default PlayerCard;
