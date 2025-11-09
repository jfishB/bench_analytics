import React from "react";

interface PlayerCardProps {
  id?: string | number;
  name: string;
  teamName?: string;
  battingPosition?: string | number | null;
  className?: string;
}

/**
 * PlayerCard
 * - player name (prominent)
 * - team name (subtle)
 * - batting position (optional, shows `--` when not provided)
 *
 * added comment where to add more fields.
 */
export default function PlayerCard({
  id,
  name,
  teamName,
  battingPosition,
  className = "",
}: PlayerCardProps) {
  return (
    <article
      data-player-id={id}
      className={
        "bg-white shadow-sm border border-gray-100 rounded-lg p-4 w-full max-w-xs " +
        className
      }
    >
      <header className="mb-2">
        <h3 className="text-lg font-semibold text-gray-900 truncate" title={name}>
          {name}
        </h3>
      </header>

      <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">Team</span>
          <span className="text-sm font-medium text-gray-800">{teamName || "--"}</span>
        </div>

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
