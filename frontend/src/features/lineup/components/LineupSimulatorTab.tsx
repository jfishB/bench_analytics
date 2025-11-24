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
import { SavedLineup, deleteLineup } from "../services/lineupService";
import { useMonteCarloSimulation } from "../hooks/useMonteCarloSimulation";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { BarChart3 } from "lucide-react";

interface LineupSimulatorTabProps {
  savedLineups: SavedLineup[];
  loading: boolean;
}

export function LineupSimulatorTab({
  savedLineups,
  loading,
}: LineupSimulatorTabProps) {
  const [selectedLineupId, setSelectedLineupId] = useState<number | null>(null);
  const [numGames, setNumGames] = useState<number>(20000);
  const [statusMessage, setStatusMessage] = useState("");
  const [showDetailedAnalysis, setShowDetailedAnalysis] = useState(false);
  const {
    comparisonResult,
    simulating,
    simulationError,
    setSimulationError,
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
    handleClearResults();
  };

  const handleClearResults = () => {
    clearResults();
    setShowDetailedAnalysis(false);
  };

  const handleRunSimulation = async () => {
    if (!selectedLineup) return;

    const playerIds = selectedLineup.players
      .sort((a, b) => a.batting_order - b.batting_order)
      .map((p) => p.player_id);

    if (playerIds.length !== 9) {
      setSimulationError(
        "Lineup must have exactly 9 players to run simulation"
      );
      return;
    }

    await runSimulation(playerIds, numGames);
  };

  const handleDeleteLineup = async (lineupId: number, e?: React.MouseEvent) => {
    e?.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this lineup?")) return;

    try {
      await deleteLineup(lineupId);
      // clear selection if deleted lineup was selected
      setSelectedLineupId((cur) => (cur === lineupId ? null : cur));
      // simple refresh: ask parent to re-fetch instead if available
      window.location.reload();
    } catch (err: any) {
      // show error (uses existing simulation error setter)
      setSimulationError?.(String(err) ?? "Failed to delete lineup");
    }
  };

  return (
    <div className="space-y-6">
      {/* Lineup Selection Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-900/10 rounded-lg">
              <BarChart3 className="h-5 w-5 text-blue-900" />
            </div>
            <div>
              <CardTitle>Monte Carlo Simulation</CardTitle>
              <CardDescription>
                Choose a saved lineup to run Monte Carlo simulation.
              </CardDescription>
            </div>
          </div>
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
                      <Button
                        onClick={(ev) => handleDeleteLineup(lineup.id, ev)}
                        variant="outline"
                        className="ml-2 bg-red-600 text-white hover:bg-red-700"
                      >
                        Delete Lineup
                      </Button>
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
                    setNumGames(parseInt(e.target.value) || 20000)
                  }
                  className="px-3 py-2 border border-gray-300 rounded-md w-32"
                  disabled={simulating}
                />
                <span className="text-sm text-gray-600">
                  (recommended: 20,000)
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
          {/* Winner Display */}
          <div className="text-center py-4">
            <h3 className="text-2xl font-bold mb-2">
              {comparisonResult.winner === "user" && "Your Lineup Wins!"}
              {comparisonResult.winner === "baseline" && "wOBA Baseline Wins"}
              {comparisonResult.winner === "tie" && "It's a Tie!"}
            </h3>
            <p className="text-lg text-gray-700">
              {comparisonResult.winner === "user" &&
                `Your lineup scores about ${Math.abs(
                  comparisonResult.difference
                ).toFixed(2)} more runs per game`}
              {comparisonResult.winner === "baseline" &&
                `Baseline scores about ${Math.abs(
                  comparisonResult.difference
                ).toFixed(2)} more runs per game`}
              {comparisonResult.winner === "tie" &&
                "Both lineups perform equally"}
            </p>
          </div>

          {/* Comparison Stats */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* User Lineup */}
            <Card>
              <CardHeader>
                <CardTitle>Your Lineup</CardTitle>
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
            <Card>
              <CardHeader>
                <CardTitle>wOBA Baseline</CardTitle>
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

          {/* Toggle Detailed Analysis Button */}
          <div className="flex justify-center">
            <Button
              onClick={() => setShowDetailedAnalysis(!showDetailedAnalysis)}
              variant="outline"
              className="gap-2"
            >
              {showDetailedAnalysis ? "Hide" : "Show"} Detailed Analysis
              <span className="text-lg">
                {showDetailedAnalysis ? "▲" : "▼"}
              </span>
            </Button>
          </div>

          {/* Detailed Analysis Section */}
          {showDetailedAnalysis && (
            <div className="space-y-4 animate-in fade-in duration-300">
              {/* Score Distribution Histogram */}
              <Card>
                <CardHeader>
                  <CardTitle>Score Distribution Comparison</CardTitle>
                  <CardDescription>
                    Overlayed histogram showing frequency of runs scored
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                      data={(() => {
                        // Combine both distributions into one dataset
                        const userDist =
                          comparisonResult.userLineup.score_distribution;
                        const baselineDist =
                          comparisonResult.baselineLineup.score_distribution;
                        const allScores = new Set([
                          ...Object.keys(userDist),
                          ...Object.keys(baselineDist),
                        ]);

                        return Array.from(allScores)
                          .map((score) => ({
                            score: parseInt(score),
                            yourLineup: userDist[score] || 0,
                            baseline: baselineDist[score] || 0,
                          }))
                          .sort((a, b) => a.score - b.score);
                      })()}
                      margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="score"
                        label={{
                          value: "Runs Scored",
                          position: "insideBottom",
                          offset: -5,
                        }}
                      />
                      <YAxis
                        label={{
                          value: "Number of Games",
                          angle: -90,
                          position: "insideLeft",
                        }}
                      />
                      <Tooltip
                        content={({ active, payload }: any) => {
                          if (active && payload && payload.length) {
                            const data = payload[0].payload;
                            return (
                              <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
                                <p className="font-semibold mb-1">
                                  {data.score} Runs
                                </p>
                                <p className="text-sm text-blue-600">
                                  Your Lineup: {data.yourLineup} games
                                </p>
                                <p className="text-sm text-gray-600">
                                  Baseline: {data.baseline} games
                                </p>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Legend verticalAlign="top" />
                      <Bar
                        dataKey="yourLineup"
                        fill="#3b82f6"
                        name="Your Lineup"
                        opacity={0.8}
                      />
                      <Bar
                        dataKey="baseline"
                        fill="#9ca3af"
                        name="wOBA Baseline"
                        opacity={0.6}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Additional Statistics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    Additional Statistics
                    <div className="group relative inline-block">
                      <button
                        className="w-5 h-5 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-xs font-semibold text-gray-600 cursor-help transition-colors"
                        type="button"
                      >
                        ?
                      </button>
                      <div className="invisible group-hover:visible absolute left-0 top-6 z-10 w-80 p-4 bg-gray-900 text-white text-sm rounded-lg shadow-xl">
                        <div className="space-y-2">
                          <div>
                            <strong className="text-blue-300">Median:</strong>{" "}
                            The middle value when all game scores are sorted.
                            Half of games scored above this, half below. Less
                            affected by outliers than the average.
                          </div>
                          <div>
                            <strong className="text-blue-300">
                              Standard Deviation:
                            </strong>{" "}
                            Measures consistency. Lower std dev means more
                            predictable scoring. Higher means more variability
                            between games.
                          </div>
                        </div>
                        <div className="absolute -top-1 left-4 w-2 h-2 bg-gray-900 rotate-45"></div>
                      </div>
                    </div>
                  </CardTitle>
                  <CardDescription>
                    Detailed performance metrics
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* User Lineup Stats */}
                    <div>
                      <h4 className="font-semibold mb-3 text-blue-700">
                        Your Lineup
                      </h4>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="p-3 bg-blue-50 rounded">
                          <div className="text-xs text-gray-600">Median</div>
                          <div className="text-xl font-bold">
                            {comparisonResult.userLineup.median_score.toFixed(
                              1
                            )}
                          </div>
                        </div>
                        <div className="p-3 bg-blue-50 rounded">
                          <div className="text-xs text-gray-600">Std Dev</div>
                          <div className="text-xl font-bold">
                            {comparisonResult.userLineup.std_dev.toFixed(2)}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Baseline Stats */}
                    <div>
                      <h4 className="font-semibold mb-3 text-gray-700">
                        wOBA Baseline
                      </h4>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="p-3 bg-gray-50 rounded">
                          <div className="text-xs text-gray-600">Median</div>
                          <div className="text-xl font-bold">
                            {comparisonResult.baselineLineup.median_score.toFixed(
                              1
                            )}
                          </div>
                        </div>
                        <div className="p-3 bg-gray-50 rounded">
                          <div className="text-xs text-gray-600">Std Dev</div>
                          <div className="text-xl font-bold">
                            {comparisonResult.baselineLineup.std_dev.toFixed(2)}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Batting Order Comparison */}
              <Card>
                <CardHeader>
                  <CardTitle>Batting Order Comparison</CardTitle>
                  <CardDescription>
                    How the lineups differ in batting order
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3 text-blue-700">
                        Your Lineup
                      </h4>
                      <div className="space-y-2">
                        {comparisonResult.userLineup.lineup.map(
                          (player, idx) => (
                            <div
                              key={idx}
                              className="flex items-center gap-2 p-2 bg-blue-50 rounded"
                            >
                              <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold">
                                {idx + 1}
                              </span>
                              <span className="text-sm">{player}</span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-3 text-gray-700">
                        wOBA Baseline
                      </h4>
                      <div className="space-y-2">
                        {comparisonResult.baselineLineup.lineup.map(
                          (player, idx) => (
                            <div
                              key={idx}
                              className="flex items-center gap-2 p-2 bg-gray-50 rounded"
                            >
                              <span className="w-6 h-6 rounded-full bg-gray-600 text-white flex items-center justify-center text-sm font-bold">
                                {idx + 1}
                              </span>
                              <span className="text-sm">{player}</span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          <div className="flex justify-center mt-4">
            <Button onClick={handleClearResults} variant="outline">
              Clear Results
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
