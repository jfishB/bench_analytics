/**
 * LineupSimulatorTab - Component for displaying all saved lineups and running Monte Carlo simulations
 */

import React, { useState, useEffect } from "react";
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
  const [statusMessage, setStatusMessage] = useState("");
  const {
    comparisonResult,
    simulating,
    simulationError,
    runSimulation,
    clearResults,
  } = useMonteCarloSimulation();

  // Cycle through status messages while simulating
  useEffect(() => {
    if (!simulating) {
      setStatusMessage("");
      return;
    }

    const messages = [
      "Simulating your lineup...",
      "Calculating runs...",
      "Tracking base runners...",
      "Recording outcomes...",
      "Sorting players by wOBA...",
      "Simulating baseline lineup...",
      "Running Monte Carlo iterations...",
      "Processing game states...",
      "Evaluating batting sequences...",
      "Analyzing scoring patterns...",
      "Computing probabilities...",
      "Comparing results...",
      "Aggregating statistics...",
    ];

    let currentIndex = 0;
    const interval = setInterval(() => {
      setStatusMessage(messages[currentIndex]);
      currentIndex = (currentIndex + 1) % messages.length;
    }, 800); // Change message every 800ms

    return () => clearInterval(interval);
  }, [simulating]);

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
                  <p className="text-sm text-gray-600 animate-pulse">
                    {statusMessage || "Initializing simulation..."}
                  </p>
                  <p className="text-xs text-gray-500">
                    {numGames.toLocaleString()} games
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

      {/* Simulation Results - Comparison */}
      {comparisonResult && (
        <div className="space-y-4">
          {/* Winner Banner */}
          <Card
            className={`${
              comparisonResult.winner === "user"
                ? "border-green-500 bg-green-50"
                : comparisonResult.winner === "baseline"
                ? "border-orange-500 bg-orange-50"
                : "border-gray-500 bg-gray-50"
            } border-2`}
          >
            <CardContent className="pt-6">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-2">
                  {comparisonResult.winner === "user" && "🏆 Your Lineup Wins!"}
                  {comparisonResult.winner === "baseline" &&
                    "📊 wOBA Baseline Wins"}
                  {comparisonResult.winner === "tie" && "🤝 It's a Tie!"}
                </h3>
                <p className="text-lg text-gray-700">
                  {comparisonResult.winner === "user" &&
                    `Your lineup scores ${Math.abs(
                      comparisonResult.difference
                    ).toFixed(2)} more runs per game`}
                  {comparisonResult.winner === "baseline" &&
                    `Baseline scores ${Math.abs(
                      comparisonResult.difference
                    ).toFixed(2)} more runs per game`}
                  {comparisonResult.winner === "tie" &&
                    "Both lineups perform equally"}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Comparison Stats */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* User Lineup */}
            <Card
              className={
                comparisonResult.winner === "user"
                  ? "ring-2 ring-green-500"
                  : ""
              }
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Your Lineup
                  {comparisonResult.winner === "user" && <span>🏆</span>}
                </CardTitle>
                <CardDescription>
                  {selectedLineup?.name || "Selected Lineup"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">
                      Average Runs per Game
                    </div>
                    <div className="text-4xl font-bold text-blue-700">
                      {comparisonResult.userLineup.avg_score.toFixed(2)}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Based on{" "}
                    {comparisonResult.userLineup.num_games.toLocaleString()}{" "}
                    simulated games
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Baseline Lineup */}
            <Card
              className={
                comparisonResult.winner === "baseline"
                  ? "ring-2 ring-orange-500"
                  : ""
              }
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  wOBA Baseline
                  {comparisonResult.winner === "baseline" && <span>🏆</span>}
                </CardTitle>
                <CardDescription>Same players, sorted by wOBA</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">
                      Average Runs per Game
                    </div>
                    <div className="text-4xl font-bold text-gray-700">
                      {comparisonResult.baselineLineup.avg_score.toFixed(2)}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Based on{" "}
                    {comparisonResult.baselineLineup.num_games.toLocaleString()}{" "}
                    simulated games
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-center">
            <Button onClick={clearResults} variant="outline">
              Clear Results
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
