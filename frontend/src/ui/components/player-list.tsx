import React from "react";
import { cn } from "../../utils";

interface PlayerListItem {
  id?: string | number;
  name: string;
  battingOrder?: number | null;
}

interface PlayerListProps {
  items: PlayerListItem[];
  className?: string;
}

/**
 * PlayerList (UI primitive)
 * Renders an ordered list of player tiles. The UI primitive expects
 * items already ordered by batting order; it will not sort them.
 */
export function PlayerList({ items, className = "" }: PlayerListProps) {
  if (!items || items.length === 0) {
    return (
      <div className={cn("text-sm text-gray-500 italic py-4", className)}>
        No players found.
      </div>
    );
  }

  return (
    <ol className={cn("space-y-2", className)}>
      {items.map((it) => (
        <li key={it.id ?? it.name}>
          <div className="flex items-center bg-white border border-gray-100 rounded-lg p-3 shadow-sm">
            <div className="w-10 flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center font-semibold text-gray-700">
                {it.battingOrder != null ? it.battingOrder : "—"}
              </div>
            </div>

            <div className="ml-3 flex-1">
              <div className="text-sm font-medium text-gray-900 truncate">{it.name}</div>
              {/* Placeholder for small meta info */}
            </div>

            {/* Optional area for extra actions or badges */}
            <div className="ml-3 text-xs text-gray-500">{/* ADDITIONAL FIELDS */}</div>
          </div>
        </li>
      ))}
    </ol>
  );
}
export default PlayerList;
