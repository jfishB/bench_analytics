/**
 * LineupSimulatorTab - Component for displaying all saved lineups and running Monte Carlo simulations
 */

import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../ui/components/card";
import { Button } from "../../../ui/components/button";
import { SavedLineup } from "../services/lineupService";
import { useMonteCarloSimulation } from "../hooks/useMonteCarloSimulation";

interface LineupSimulatorTabProps {
  savedLineups: SavedLineup[];
  loading: boolean;
}

export function LineupSimulatorTab({
  savedLineups,
  loading,
}: LineupSimulatorTabProps) {
  const [selectedLineupId, setSelectedLineupId] = useState<number | null>(null);
  const [numGames, setNumGames] = useState<number>(10000);
  const {
    simulationResult,
    simulating,
    simulationError,
    runSimulation,
    clearResults,
  } = useMonteCarloSimulation();

  const selectedLineup = savedLineups.find((l) => l.id === selectedLineupId);

  const handleSelectLineup = (lineupId: number) => {
    setSelectedLineupId(lineupId);
    clearResults();
  };

  const handleRunSimulation = async () => {
    if (!selectedLineup) return;

    const playerIds = selectedLineup.players
      .sort((a, b) => a.batting_order - b.batting_order)
      .map((p) => p.player_id);

    if (playerIds.length !== 9) {
      alert("Lineup must have exactly 9 players to run simulation");
      return;
    }

    await runSimulation(playerIds, numGames);
  };

  return (
    <div className="space-y-6">
      {/* Lineup Selection Section */}
      <Card>
        <CardHeader>
          <CardTitle>Select a Lineup</CardTitle>
          <CardDescription>
            Choose a saved lineup to run Monte Carlo simulation
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
                  className={`cursor-pointer transition-all ${
                    selectedLineupId === lineup.id
                      ? "ring-2 ring-primary shadow-lg"
                      : "hover:shadow-lg"
                  }`}
                  onClick={() => handleSelectLineup(lineup.id)}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">{lineup.name}</CardTitle>
                    <CardDescription className="text-xs">
                      Created:{" "}
                      {new Date(lineup.created_at).toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-gray-700 mb-2">
                        Batting Order:
                      </div>
                      <div className="space-y-1">
                        {(lineup.players ?? [])
                          .sort((a, b) => a.batting_order - b.batting_order)
                          .map((player) => (
                            <div
                              key={player.player_id}
                              className="flex items-center text-sm"
                            >
                              <span className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-semibold mr-2">
                                {player.batting_order}
                              </span>
                              <span className="flex-1">
                                {player.player_name}
                              </span>
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

      {/* Simulation Controls */}
      {selectedLineup && (
        <Card>
          <CardHeader>
            <CardTitle>Run Simulation</CardTitle>
            <CardDescription>
              Simulate {selectedLineup.name} using Monte Carlo method
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <label htmlFor="numGames" className="text-sm font-medium">
                  Number of games:
                </label>
                <input
                  id="numGames"
                  type="number"
                  min="100"
                  max="100000"
                  step="100"
                  value={numGames}
                  onChange={(e) =>
                    setNumGames(parseInt(e.target.value) || 1000)
                  }
                  className="px-3 py-2 border border-gray-300 rounded-md w-32"
                  disabled={simulating}
                />
                <span className="text-sm text-gray-600">
                  (recommended: 10,000)
                </span>
              </div>

              <Button
                onClick={handleRunSimulation}
                disabled={simulating || !selectedLineup}
              >
                {simulating ? "Simulating..." : "Run Simulation"}
              </Button>

              {simulating && (
                <div className="space-y-2">
                  <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                    <div className="bg-primary h-2.5 rounded-full animate-pulse w-full"></div>
                  </div>
                  <p className="text-sm text-gray-600">
                    Running {numGames.toLocaleString()} simulated games...
                  </p>
                </div>
              )}

              {simulationError && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800">
                    <strong>Error:</strong> {simulationError}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Simulation Results */}
      {simulationResult && (
        <Card>
          <CardHeader>
            <CardTitle>Simulation Results</CardTitle>
            <CardDescription>
              Results from {simulationResult.num_games.toLocaleString()}{" "}
              simulated games
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Avg Score</div>
                  <div className="text-2xl font-bold text-primary">
                    {simulationResult.avg_score.toFixed(2)}
                  </div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Median</div>
                  <div className="text-2xl font-bold">
                    {simulationResult.median_score.toFixed(1)}
                  </div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Std Dev</div>
                  <div className="text-2xl font-bold">
                    {simulationResult.std_dev.toFixed(2)}
                  </div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Min</div>
                  <div className="text-2xl font-bold text-red-600">
                    {simulationResult.min_score}
                  </div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Max</div>
                  <div className="text-2xl font-bold text-green-600">
                    {simulationResult.max_score}
                  </div>
                </div>
              </div>

              <Button onClick={clearResults} variant="outline">
                Clear Results
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
