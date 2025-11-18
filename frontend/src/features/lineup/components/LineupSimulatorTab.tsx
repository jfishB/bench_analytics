/**
 * LineupSimulatorTab - Component for displaying all saved lineups
 */

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../ui/components/card";
import { SavedLineup } from "../services/lineupService";

interface LineupSimulatorTabProps {
  savedLineups: SavedLineup[];
  loading: boolean;
}

export function LineupSimulatorTab({
  savedLineups,
  loading,
}: LineupSimulatorTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Lineup Simulator</CardTitle>
        <CardDescription>
          View and simulate all your saved lineups
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center text-muted-foreground py-8">
            Loading lineups...
          </div>
        ) : savedLineups.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            <div className="mb-4">
              <svg
                className="h-16 w-16 text-gray-400 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No Saved Lineups Yet
            </h3>
            <p className="text-sm text-gray-600">
              Create and save lineups in the Generate Lineup tab to see them
              here.
            </p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {savedLineups.map((lineup) => (
              <Card
                key={lineup.id}
                className="hover:shadow-lg transition-shadow"
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">{lineup.name}</CardTitle>
                  <CardDescription className="text-xs">
                    Created: {new Date(lineup.created_at).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-700 mb-2">
                      Batting Order:
                    </div>
                    <div className="space-y-1">
                      {lineup.players
                        ?.sort((a, b) => a.batting_order - b.batting_order)
                        .map((player) => (
                          <div
                            key={player.player_id}
                            className="flex items-center text-sm"
                          >
                            <span className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-semibold mr-2">
                              {player.batting_order}
                            </span>
                            <span className="flex-1">{player.player_name}</span>
                          </div>
                        ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
