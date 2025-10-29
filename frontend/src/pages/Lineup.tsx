import { useState } from "react";
import { Button } from "../components/ui/button";

const ROSTER_BASE = "http://localhost:8000/api/v1/roster";
const LINEUPS_BASE = "http://localhost:8000/api/v1/lineups";

interface Player {
  id: number;
  name: string;
  xwoba: number;
  bb_percent: number;
  k_percent: number;
  barrel_batted_rate: number;
  wos_score?: number;
}

export default function Lineup() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const [isSorted, setIsSorted] = useState(false);

  const fetchPlayers = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${ROSTER_BASE}/players/`);
      const data = await response.json();
      setPlayers(data.players || []);
      setIsSorted(false);
    } catch (error) {
      console.error("Error fetching players:", error);
    } finally {
      setLoading(false);
    }
  };

  const optimizeLineup = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${ROSTER_BASE}/players/ranked/`);
      const data = await response.json();
      setPlayers(data.players || []);
      setIsSorted(true);
    } catch (error) {
      console.error("Error optimizing lineup:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center mt-10 space-y-4 px-4">
      <h2 className="text-3xl font-bold">Lineup Optimizer</h2>
      
      <div className="max-w-2xl text-center text-sm text-gray-600 bg-blue-50 border border-blue-200 rounded p-3">
        <p className="font-semibold mb-1">Weighted Offensive Score (WOS) - Placeholder Algorithm</p>
        <p className="text-xs">
          Formula: <code className="bg-white px-1 py-0.5 rounded">1000 × xwOBA + 2 × BB% + Barrel% - 0.5 × K%</code>
        </p>
        <p className="text-xs mt-1">
          This is a simplified scoring method used for demonstration purposes.
        </p>
      </div>

      <div className="flex gap-4">
        <Button onClick={fetchPlayers} disabled={loading} variant="outline">
          {loading ? "Loading..." : "Load All Players"}
        </Button>
        
        {players.length > 0 && !isSorted && (
          <Button onClick={optimizeLineup} disabled={loading} variant="outline">
            Optimize Lineup
          </Button>
        )}
      </div>

      {isSorted && (
        <div className="bg-gray-50 border border-gray-200 text-gray-700 px-4 py-2 rounded text-sm">
          Sorted by WOS
        </div>
      )}

      {players.length > 0 && (
        <div className="w-full max-w-6xl overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-300 text-sm">
            <thead className="bg-gray-100">
              <tr>
                {isSorted && <th className="px-4 py-2 border">Rank</th>}
                <th className="px-4 py-2 border">Player Name</th>
                <th className="px-4 py-2 border">xwOBA</th>
                <th className="px-4 py-2 border">BB%</th>
                <th className="px-4 py-2 border">K%</th>
                <th className="px-4 py-2 border">Barrel%</th>
                {isSorted && <th className="px-4 py-2 border">WOS Score</th>}
              </tr>
            </thead>
            <tbody>
              {players.map((player, idx) => (
                <tr key={player.id} className="hover:bg-gray-50">
                  {isSorted && (
                    <td className="px-4 py-2 border text-center font-semibold">
                      {idx + 1}
                    </td>
                  )}
                  <td className="px-4 py-2 border">{player.name}</td>
                  <td className="px-4 py-2 border text-center">
                    {player.xwoba?.toFixed(3) || "—"}
                  </td>
                  <td className="px-4 py-2 border text-center">
                    {player.bb_percent?.toFixed(1) || "—"}
                  </td>
                  <td className="px-4 py-2 border text-center">
                    {player.k_percent?.toFixed(1) || "—"}
                  </td>
                  <td className="px-4 py-2 border text-center">
                    {player.barrel_batted_rate?.toFixed(1) || "—"}
                  </td>
                  {isSorted && (
                    <td className="px-4 py-2 border text-center font-bold text-blue-600">
                      {player.wos_score?.toFixed(2) || "—"}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {players.length === 0 && !loading && (
        <p className="text-gray-500">Click "Load All Players" to get started</p>
      )}
    </div>
  );
}
