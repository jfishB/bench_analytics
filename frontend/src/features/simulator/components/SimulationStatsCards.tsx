/**
 * Display key simulation statistics in card format
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/components/card';
import { SimulationResult } from '../types';

interface SimulationStatsCardsProps {
  result: SimulationResult;
}

export const SimulationStatsCards: React.FC<SimulationStatsCardsProps> = ({ result }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Average Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{result.avg_score.toFixed(2)}</div>
          <p className="text-xs text-muted-foreground">runs per game</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Median Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{result.median_score}</div>
          <p className="text-xs text-muted-foreground">most common</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Std Deviation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">±{result.std_dev.toFixed(2)}</div>
          <p className="text-xs text-muted-foreground">variability</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Score Range</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{result.min_score} - {result.max_score}</div>
          <p className="text-xs text-muted-foreground">min to max</p>
        </CardContent>
      </Card>
    </div>
  );
};
