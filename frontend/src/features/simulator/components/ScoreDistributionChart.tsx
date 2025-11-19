/**
 * Bar chart showing distribution of scores across simulated games
 */

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { SimulationResult } from '../types';

interface ScoreDistributionChartProps {
  result: SimulationResult;
}

export const ScoreDistributionChart: React.FC<ScoreDistributionChartProps> = ({ result }) => {
  // Convert distribution to chart data
  const chartData = Object.entries(result.score_distribution)
    .map(([score, count]) => ({
      score: parseInt(score),
      count,
      percentage: ((count / result.num_games) * 100).toFixed(1),
    }))
    .sort((a, b) => a.score - b.score);

  // Color bars based on score (green for high, yellow for medium, red for low)
  const getColor = (score: number) => {
    if (score >= 8) return '#22c55e'; // green
    if (score >= 4) return '#3b82f6'; // blue
    if (score >= 2) return '#eab308'; // yellow
    return '#ef4444'; // red
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
          <p className="font-semibold">{data.score} runs</p>
          <p className="text-sm text-gray-600">{data.count.toLocaleString()} games</p>
          <p className="text-sm text-gray-600">{data.percentage}% of total</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="score" 
            label={{ value: 'Runs Scored', position: 'insideBottom', offset: -10 }}
          />
          <YAxis 
            label={{ value: 'Number of Games', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.score)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
