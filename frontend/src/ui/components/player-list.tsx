import React from "react";
import { cn } from "../../utils";
import type { Player } from "../../shared/types";

export interface PlayerListItem {
  id?: string;
  name: string;
  battingOrder?: number | null;
  // Payload may be partial player data
  payload: Partial<Player>;
  isSelected?: boolean;
}

/**
 * Extract initials from a player name.
 * Handles formats like "Last, First" or "Last, First Middle"
 * Returns first letter of first name and first letter of last name.
 */
function getPlayerInitials(name: string): string {
  if (!name) return "—";

  // Handle format: "Last, First" or "Last, First Middle"
  const parts = name.split(",").map((s) => s.trim());

  if (parts.length < 2) {
    // Fallback: just use first two letters of the name
    return name.substring(0, 2).toUpperCase();
  }

  const lastName = parts[0];
  const firstName = parts[1];

  // Handle hyphenated last names (e.g., "Kiner-Falefa")
  const lastNameParts = lastName.split(/[-\s]+/);
  const firstNameParts = firstName.split(/\s+/);

  // Get first initial of first name
  const firstInitial = firstNameParts[0]?.[0] || "";

  // Get first initial of last name (or initials if hyphenated)
  let lastInitials = "";
  if (lastNameParts.length > 1) {
    // Hyphenated last name: use initials of each part
    lastInitials = lastNameParts.map((part) => part[0]).join("");
  } else {
    lastInitials = lastName[0] || "";
  }

  return (firstInitial + lastInitials).toUpperCase();
}

export interface PlayerListProps {
  items: PlayerListItem[];
  className?: string;
  onItemClick?: (item: PlayerListItem) => void;
  badgeClassName?: string;
  onSelectionToggle?: (item: PlayerListItem) => void;
  showCheckboxes?: boolean;
  showInitials?: boolean;
}

/**
 * PlayerList (UI primitive)
 *
 * Renders an ordered list of player tiles.
 * - Expects items already sorted by batting order; does not sort internally.
 * - Displays player initials (default) or batting order numbers in badge, player name, and optional meta/actions area.
 * - Shows fallback text if the list is empty.
 */
export function PlayerList({
  items,
  className = "",
  onItemClick,
  badgeClassName = "bg-primary text-white dark:bg-primary",
  onSelectionToggle,
  showCheckboxes = false,
  showInitials = true,
}: PlayerListProps) {
  // Empty state: display friendly fallback
  if (!items || items.length === 0) {
    return (
      <div className={cn("text-sm text-gray-500 italic py-4", className)}>
        No players found.
      </div>
    );
  }

  // Render ordered list of players
  return (
    <ol className={cn("space-y-2", className)}>
      {items.map((it) => (
        <li key={it.id ?? it.name}>
          <div
            role={onItemClick ? "button" : undefined}
            tabIndex={onItemClick ? 0 : undefined}
            onClick={onItemClick ? () => onItemClick(it) : undefined}
            onKeyDown={
              onItemClick
                ? (e: React.KeyboardEvent) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onItemClick(it);
                    }
                  }
                : undefined
            }
            className={cn(
              "group relative overflow-hidden bg-white border rounded-xl p-3 transition-all shadow-sm",
              onItemClick &&
                "cursor-pointer hover:shadow-md border-blue-100 hover:border-blue-300"
            )}
          >
            {onItemClick && (
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-blue-500/20 to-blue-500/0 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            )}
            <div className="relative flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center text-white shadow-md bg-gradient-to-br from-blue-600 to-blue-800",
                  badgeClassName
                )}>
                  <span className="text-sm font-semibold">
                    {showInitials
                      ? getPlayerInitials(it.name)
                      : it.battingOrder != null
                      ? it.battingOrder
                      : "—"}
                  </span>
                </div>
                <div>
                  <div className="font-medium">{it.name}</div>
                </div>
              </div>

              {/* Optional area for extra actions or badges */}
              {showCheckboxes && onSelectionToggle && (
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={it.isSelected || false}
                    onChange={(e) => {
                      e.stopPropagation();
                      onSelectionToggle(it);
                    }}
                    className="h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
              )}
            </div>
          </div>
        </li>
      ))}
    </ol>
  );
}

export default PlayerList;
