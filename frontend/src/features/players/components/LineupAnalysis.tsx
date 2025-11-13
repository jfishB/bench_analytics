import React from "react";
import { cn } from "../../../utils";
import type { Player } from "../../../shared/types";

export interface LineupAnalysisProps {
  player: {
    id?: string;
    name: string;
    payload: Partial<Player>;
  };
  onClick?: (player: LineupAnalysisProps["player"]) => void;
  badgeClassName?: string;
  className?: string;
  battingOrder?: number | null;
  message?: string;
}

export function LineupAnalysis({
  player,
  onClick,
  badgeClassName = "bg-primary text-white dark:bg-primary",
  className = "",
  battingOrder,
  message,
}: LineupAnalysisProps) {
  return (
    <div
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={onClick ? () => onClick(player) : undefined}
      onKeyDown={
        onClick
          ? (e: React.KeyboardEvent) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick(player);
              }
            }
          : undefined
      }
      className={cn(
        "flex flex-col bg-white border border-gray-100 rounded-lg p-3 shadow-sm",
        onClick && "cursor-pointer",
        className
      )}
    >
      <div className="flex items-center">
        <div className="w-10 flex-shrink-0">
          <div
            className={cn(
              badgeClassName,
              "h-8 w-8 rounded-full flex items-center justify-center font-semibold"
            )}
          >
            {battingOrder != null ? battingOrder : "—"}
          </div>
        </div>

        <div className="ml-3 flex-1 flex items-center">
          <div className="text-sm font-medium text-gray-900 truncate w-[300px]">
            {player.name}
          </div>
          <div className="text-sm italic text-gray-500 truncate ml-4">
            {message}
          </div>
        </div>
      </div>
    </div>
  );
}

export default LineupAnalysis;