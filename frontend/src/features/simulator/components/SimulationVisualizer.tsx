/**
 * Main component for Monte Carlo simulation visualization
 * Displays lineup, runs simulation, and shows results with charts
 */

import React, { useState } from 'react';
import { Button } from '../../../ui/components/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../ui/components/card';
import { useSimulation } from '../hooks';
import { SimulationStatsCards } from './SimulationStatsCards';
import { ScoreDistributionChart } from './ScoreDistributionChart';
import { LineupDisplay } from './LineupDisplay';
import { Player } from '../types';

interface SimulationVisualizerProps {
  players: Player[];
}

export const SimulationVisualizer: React.FC<SimulationVisualizerProps> = ({ players }) => {
  const { simulationResult, isLoading, error, runSimulationByIds, clearResults } = useSimulation();
  const [numGames, setNumGames] = useState(10000);

  const handleRunSimulation = () => {
    if (players.length !== 9) {
      alert('Please select exactly 9 players for the lineup');
      return;
    }

    const playerIds = players.map(p => p.id);
    runSimulationByIds(playerIds, numGames);
  };

  const handleDownloadResults = () => {
    if (!simulationResult) return;

    const csv = [
      ['Score', 'Frequency', 'Percentage'],
      ...Object.entries(simulationResult.score_distribution).map(([score, count]) => [
        score,
        count.toString(),
        ((count / simulationResult.num_games) * 100).toFixed(2) + '%'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `simulation-results-${Date.now()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Monte Carlo Simulation</CardTitle>
          <CardDescription>
            Run thousands of simulated games to predict lineup performance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Configuration */}
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">
                Number of Games to Simulate
              </label>
              <input
                type="number"
                min="100"
                max="100000"
                step="1000"
                value={numGames}
                onChange={(e) => setNumGames(parseInt(e.target.value) || 10000)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                More games = more accurate results (recommended: 10,000+)
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleRunSimulation}
                disabled={isLoading || players.length !== 9}
                className="min-w-[120px]"
              >
                {isLoading ? '⚙️ Running...' : '🎲 Run Simulation'}
              </Button>
              {simulationResult && (
                <Button
                  variant="outline"
                  onClick={clearResults}
                  disabled={isLoading}
                >
                  Clear
                </Button>
              )}
            </div>
          </div>

          {/* Player count validation */}
          {players.length !== 9 && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md text-yellow-800 text-sm">
              ⚠️ Please select exactly 9 players. Currently selected: {players.length}
            </div>
          )}

          {/* Error display */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-800 text-sm">
              ❌ {error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Display */}
      {simulationResult && (
        <div className="space-y-6 animate-in fade-in duration-500">
          {/* Lineup */}
          <LineupDisplay lineup={simulationResult.lineup} />

          {/* Statistics Cards */}
          <SimulationStatsCards result={simulationResult} />

          {/* Score Distribution Chart */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Score Distribution</CardTitle>
                  <CardDescription>
                    Runs scored across {simulationResult.num_games.toLocaleString()} simulated games
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={handleDownloadResults}>
                  📥 Download CSV
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ScoreDistributionChart result={simulationResult} />
              
              {/* Interpretation */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
                <h4 className="font-semibold text-blue-900 mb-2">💡 Interpretation</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>
                    • This lineup is expected to score <strong>{simulationResult.avg_score.toFixed(2)} runs per game</strong> on average
                  </li>
                  <li>
                    • Most games ({simulationResult.median_score} runs) fall near the median
                  </li>
                  <li>
                    • Typical variation is ±{simulationResult.std_dev.toFixed(2)} runs (1 standard deviation)
                  </li>
                  <li>
                    • Score range: {simulationResult.min_score} to {simulationResult.max_score} runs
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Help Text */}
      {!simulationResult && !isLoading && players.length === 9 && (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-4xl mb-2">🎲</div>
              <h3 className="text-lg font-semibold mb-2">Ready to Simulate!</h3>
              <p className="text-sm text-gray-600">
                Click "Run Simulation" to see how this lineup performs over {numGames.toLocaleString()} games
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
