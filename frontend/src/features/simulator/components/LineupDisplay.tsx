/**
 * Display the batting lineup with order
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../ui/components/card';

interface LineupDisplayProps {
  lineup: string[];
}

export const LineupDisplay: React.FC<LineupDisplayProps> = ({ lineup }) => {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Batting Lineup</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          {lineup.map((player, index) => (
            <div
              key={index}
              className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full font-bold mr-3">
                {index + 1}
              </div>
              <div className="font-medium">{player}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
