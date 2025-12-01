/**
 * LineupSimulatorTab - Component for displaying all saved lineups and running Monte Carlo simulations
 */

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../ui/components/card";
import { Button } from "../../../ui/components/button";
import { SavedLineup } from "../services/lineupService";
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
import { CHART_COLORS } from "../../../shared/designTokens";
import { SIMULATION_CONFIG, UI_MESSAGES } from "../../../shared/constants";
import { BarChart3, ChevronDown, ChevronRight } from "lucide-react";
import { useLineupSimulator } from "../hooks/useLineupSimulator";

interface LineupSimulatorTabProps {
  savedLineups: SavedLineup[];
  loading: boolean;
}

export function LineupSimulatorTab({
  savedLineups,
  loading,
}: LineupSimulatorTabProps) {
  const {
    selectedLineupIds,
    expandedLineupIds,
    includeWobaBaseline,
    numGames,
    statusMessage,
    results,
    simulating,
    simulationError,
    setIncludeWobaBaseline,
    setNumGames,
    handleToggleLineup,
    toggleExpandLineup,
    handleRunSimulation,
    handleDeleteLineup,
    handleClearResults,
  } = useLineupSimulator(savedLineups);

  // Returns a distinct color for each index, using the palette for the first 8, then generating new HSL colors as needed
  function getColor(index: number): string {
    if (index < CHART_COLORS.length) {
      return CHART_COLORS[index];
    }
    // Generate a new color using HSL for additional indices
    const hue = (index * 47) % 360; // 47 is a prime to help spread hues
    return `hsl(${hue}, 65%, 55%)`;
  }

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
                Choose one or more lineups to simulate and compare performance
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center text-muted-foreground py-8">
              {UI_MESSAGES.LOADING}
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
                {UI_MESSAGES.NO_LINEUPS.TITLE}
              </h3>
              <p className="text-sm text-gray-600">
                {UI_MESSAGES.NO_LINEUPS.DESCRIPTION}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {savedLineups.map((lineup) => {
                const isSelected = selectedLineupIds.includes(lineup.id);
                const isExpanded = expandedLineupIds.includes(lineup.id);
                return (
                  <div
                    key={lineup.id}
                    className={`border rounded-lg transition-all ${
                      isSelected
                        ? "border-blue-900 bg-blue-50/30"
                        : "border-gray-200 bg-white hover:border-gray-300"
                    }`}
                  >
                    {/* Header - Always Visible */}
                    <div className="flex items-center justify-between p-4">
                      <div className="flex items-center gap-3 flex-1">
                        <button
                          onClick={() => toggleExpandLineup(lineup.id)}
                          className="text-gray-400 hover:text-gray-600 transition-colors"
                        >
                          {isExpanded ? (
                            <ChevronDown className="h-5 w-5" />
                          ) : (
                            <ChevronRight className="h-5 w-5" />
                          )}
                        </button>
                        <div
                          className="flex-1 cursor-pointer"
                          onClick={() => handleToggleLineup(lineup.id)}
                        >
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-gray-900">
                              {lineup.name}
                            </h3>
                            {isSelected && (
                              <span className="bg-blue-900 text-white text-xs px-2 py-0.5 rounded-full">
                                Selected
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-500 mt-0.5">
                            {new Date(lineup.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <Button
                        onClick={(ev) => handleDeleteLineup(lineup.id, ev)}
                        variant="ghost"
                        size="sm"
                        className="text-gray-400 hover:text-red-600 hover:bg-red-50"
                      >
                        Delete
                      </Button>
                    </div>

                    {/* Expanded Content - Players List */}
                    {isExpanded && (
                      <div className="px-4 pb-4 pt-2 border-t border-gray-100">
                        <div className="space-y-1">
                          <div className="text-lg font-semibold text-gray-700 mb-2">
                            Batting Order:
                          </div>
                          {(lineup.players ?? [])
                            .sort((a, b) => a.batting_order - b.batting_order)
                            .map((player) => (
                              <div
                                key={player.player_id}
                                className="flex items-center py-0.5 gap-2"
                              >
                                <span className="w-7 h-7 rounded-full bg-blue-900 text-white flex items-center justify-center text-sm font-semibold">
                                  {player.batting_order}
                                </span>
                                <span className="flex-1 truncate text-base font-semibold">
                                  {player.player_name}
                                </span>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Simulation Controls */}
      {selectedLineupIds.length > 0 && (
        <Card className="shadow-md border-primary/20">
          <CardHeader className="pb-4">
            <CardTitle>Run Simulation</CardTitle>
            <CardDescription>
              Simulate {selectedLineupIds.length} selected lineup
              {selectedLineupIds.length !== 1 ? "s" : ""}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap items-end gap-6">
              <div className="space-y-2">
                <label htmlFor="numGames" className="text-sm font-medium">
                  Games per lineup:
                </label>
                <div className="flex items-center gap-2">
                  <input
                    id="numGames"
                    type="number"
                    min={SIMULATION_CONFIG.MIN_GAMES}
                    max={SIMULATION_CONFIG.MAX_GAMES}
                    step={SIMULATION_CONFIG.STEP_SIZE}
                    value={numGames}
                    onChange={(e) =>
                      setNumGames(
                        parseInt(e.target.value) ||
                          SIMULATION_CONFIG.DEFAULT_NUM_GAMES
                      )
                    }
                    className="px-3 py-2 border border-gray-300 rounded-md w-32"
                    disabled={simulating}
                  />
                  <span className="text-xs text-gray-500">
                    (rec: {SIMULATION_CONFIG.RECOMMENDED_GAMES.toLocaleString()}
                    )
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2 pb-3">
                <input
                  type="checkbox"
                  id="includeBaseline"
                  checked={includeWobaBaseline}
                  onChange={(e) => setIncludeWobaBaseline(e.target.checked)}
                  className="h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary"
                  disabled={simulating}
                />
                <label
                  htmlFor="includeBaseline"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Include wOBA Baseline Comparison
                </label>
              </div>

              <Button
                onClick={handleRunSimulation}
                disabled={simulating}
                className="min-w-[150px]"
              >
                {simulating ? "Simulating..." : "Run Simulation"}
              </Button>
            </div>

            {simulating && (
              <div className="mt-4 space-y-2">
                <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                  <div className="bg-primary h-2.5 rounded-full animate-pulse w-full"></div>
                </div>
                <p className="text-sm text-gray-600 animate-pulse text-center">
                  {statusMessage || UI_MESSAGES.INITIALIZING}
                </p>
              </div>
            )}

            {simulationError && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">
                  <strong>Error:</strong> {simulationError}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Simulation Results */}
      {results.length > 0 && (
        <div className="space-y-6 animate-in fade-in duration-500">
          {/* Winner Banner */}
          <div className="text-center py-6 px-4 border-2 border-primary rounded-lg shadow-lg bg-gradient-to-br from-blue-50 to-white">
            <h3 className="text-3xl font-bold mb-3">
              Winner: {results[0].name}
            </h3>
            <p className="text-xl text-gray-700 mb-1">
              Averages {results[0].avg_score.toFixed(2)} runs per game
            </p>
            {results.length > 1 && (
              <p className="text-base text-gray-600 mt-3">
                {Math.abs(results[0].avg_score - results[1].avg_score) < 0.01
                  ? `Essentially tied with ${results[1].name}`
                  : `+${(results[0].avg_score - results[1].avg_score).toFixed(
                      2
                    )} runs better than ${results[1].name}`}
              </p>
            )}
          </div>

          {/* Comparison Table */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                    <tr>
                      <th className="px-6 py-3">Rank</th>
                      <th className="px-6 py-3">Lineup Name</th>
                      <th className="px-6 py-3">Avg Runs</th>
                      <th className="px-6 py-3">Median</th>
                      <th className="px-6 py-3">Std Dev</th>
                      <th className="px-6 py-3">Min/Max</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((res, idx) => (
                      <tr
                        key={res.id}
                        className={`border-b ${
                          idx === 0 ? "bg-blue-50/50 font-medium" : "bg-white"
                        }`}
                      >
                        <td className="px-6 py-4">#{idx + 1}</td>
                        <td className="px-6 py-4 font-medium text-gray-900">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{
                                backgroundColor: getColor(idx),
                              }}
                            ></div>
                            {res.name}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-base">
                          {res.avg_score.toFixed(2)}
                        </td>
                        <td className="px-6 py-4">
                          {res.median_score.toFixed(1)}
                        </td>
                        <td className="px-6 py-4">{res.std_dev.toFixed(2)}</td>
                        <td className="px-6 py-4 text-gray-500">
                          {res.min_score} - {res.max_score}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Charts Section */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Score Distribution */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Score Distribution Comparison</CardTitle>
                <CardDescription>
                  Frequency of runs scored per game
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart
                    data={(() => {
                      // Aggregate all unique scores
                      const allScores = new Set<string>();
                      results.forEach((r) => {
                        Object.keys(r.score_distribution).forEach((s) =>
                          allScores.add(s)
                        );
                      });

                      // Create data points
                      return Array.from(allScores)
                        .map((score) => {
                          const point: any = { score: parseInt(score) };
                          results.forEach((r) => {
                            point[r.name] = r.score_distribution[score] || 0;
                          });
                          return point;
                        })
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
                        offset: -15,
                      }}
                    />
                    <YAxis
                      label={{
                        value: "Games",
                        angle: -90,
                        position: "insideLeft",
                        offset: 10,
                      }}
                    />
                    <Tooltip />
                    <Legend verticalAlign="top" />
                    {results.map((res, idx) => (
                      <Bar
                        key={res.id}
                        dataKey={res.name}
                        fill={getColor(idx)}
                        opacity={0.7}
                        maxBarSize={50}
                      />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="flex justify-center pt-4">
            <Button onClick={handleClearResults} variant="outline">
              Clear Results & Start Over
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
