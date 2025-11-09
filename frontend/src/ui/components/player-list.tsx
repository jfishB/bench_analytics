import React from "react";

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
export default function PlayerList({ items, className = "" }: PlayerListProps) {
  return (
    <ol className={"space-y-2 " + className}>
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
