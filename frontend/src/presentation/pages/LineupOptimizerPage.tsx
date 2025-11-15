import React, { useEffect, useState } from "react";
import { Button } from "../../ui/components/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../ui/components/card";
import PlayersOrderedList from "../../features/players/components/PlayersOrderedList";
import { PlayerCard } from "../../ui/components/player-card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../../ui/components/tabs";

const API_BASE =
  process.env.REACT_APP_API_BASE || "http://localhost:8000/api/v1";
const ROSTER_BASE = `${API_BASE}/roster`;

// Simple debugging page: fetch roster players and display basic status

// Main page: tabs with Roster, Optimizer (generate) and Analysis
export function LineupOptimizer() {
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<any | null>(null);

  // lineup generation states
  const [lineupPlayers, setLineupPlayers] = useState<any[]>([]);
  const [generatedLineup, setGeneratedLineup] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [teamId, setTeamId] = useState<number | undefined>(1);

  useEffect(() => {
    let cancelled = false;
    async function fetchPlayers() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${ROSTER_BASE}/players/`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const raw = Array.isArray(data)
          ? data
          : data.players ?? data.results ?? [];
        if (!cancelled) {
          setPlayers(raw);
          // initialize lineupPlayers to the roster mapping shape the list expects
          setLineupPlayers(
            raw.map((p: any) => ({
              id: p.id,
              name: p.name,
              position: p.position,
              team: String(p.team),
              batting_order: p.batting_order,
            }))
          );
          // detect team id if available
          if (raw.length > 0) {
            const first = raw[0];
            if (typeof first.team === "number") setTeamId(first.team);
            else if (first.team_id) setTeamId(first.team_id);
          }
        }
      } catch (err: any) {
        if (!cancelled) setError(err?.message ?? String(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchPlayers();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl mb-2 text-primary">Lineup Optimizer</h1>
        <p className="text-muted-foreground">
          Generate optimal batting orders based on player statistics and game
          situations
        </p>
      </div>

      <Tabs defaultValue="current" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="current">Current Roster</TabsTrigger>
          <TabsTrigger value="optimizer">Generate Lineup</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
        </TabsList>

        {/* CURRENT ROSTER */}
        <TabsContent value="current" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Team Roster</CardTitle>
              <CardDescription>
                Current players and their key statistics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4 h-full">
                <div className="w-full">
                  {loading ? (
                    <div className="text-sm">Loading roster…</div>
                  ) : error ? (
                    <div className="mb-2 text-sm text-red-600">
                      Failed to load roster: {error}{" "}
                      <Button onClick={() => window.location.reload()}>
                        Retry
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="mb-2 text-sm">
                        Loaded {players.length} players.
                      </div>
                      <div className="overflow-y-auto max-h-[400px]">
                        <PlayersOrderedList
                          players={players.map((p) => ({
                            id: p.id,
                            name: p.name,
                            position: p.position,
                            team: String(p.team),
                            batting_order: p.batting_order,
                          }))}
                          onItemClick={(p) =>
                            setSelected(
                              players.find((x) => x.id === p.id) ?? null
                            )
                          }
                        />
                      </div>
                    </>
                  )}
                </div>

                <div className="h-full flex items-start">
                  {selected ? (
                    <div className="w-full">
                      <PlayerCard
                        id={selected.id}
                        name={selected.name}
                        teamID={String(selected.team)}
                        battingPosition={selected.position}
                        className="w-full"
                      />

                      <div className="mt-3 bg-gray-50 border rounded p-3 text-sm">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <div className="text-xs text-gray-500">xwOBA</div>
                            <div className="font-medium">
                              {selected.xwoba ?? "—"}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">BB %</div>
                            <div className="font-medium">
                              {selected.bb_percent ?? "—"}%
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">K %</div>
                            <div className="font-medium">
                              {selected.k_percent ?? "—"}%
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">
                              Barrel %
                            </div>
                            <div className="font-medium">
                              {selected.barrel_batted_rate ?? "—"}%
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 italic py-6">
                      Select a player to view details.
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* LINEUP OPTIMIZER */}
        <TabsContent value="optimizer" className="space-y-4">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Lineup Optimizer</CardTitle>
                <CardDescription>
                  Generate an optimal batting order based on current roster
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">
                  Use the tester below to call the backend generator.
                </div>
                <div className="pt-4">
                  <PlayersOrderedList
                    players={lineupPlayers}
                    onItemClick={(p) =>
                      setSelected(players.find((x) => x.id === p.id) ?? null)
                    }
                    badgeClassName="bg-primary text-white dark:bg-primary"
                  />
                  <div className="pt-4">
                    <Button
                      onClick={async () => {
                        setGenerating(true);
                        try {
                          const payload = { team_id: teamId };
                          const res = await fetch(`${API_BASE}/lineups/`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(payload),
                          });
                          if (!res.ok) throw new Error(`HTTP ${res.status}`);
                          const data = await res.json();
                          const ordered = (data.players || []).map((p: any) => {
                            const full = players.find(
                              (r) => r.id === p.player_id
                            ) || {
                              id: p.player_id,
                              name: p.player_name ?? "Unknown",
                              position: p.position,
                              team: String(p.team ?? teamId),
                            };
                            return { ...full, batting_order: p.batting_order };
                          });
                          setGeneratedLineup(ordered);
                        } catch (err: any) {
                          console.error("Lineup generation failed:", err);
                        } finally {
                          setGenerating(false);
                        }
                      }}
                    >
                      {generating ? "Generating…" : "Generate Lineup"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Generated Lineup</CardTitle>
                <CardDescription>
                  Results from the backend generator
                </CardDescription>
              </CardHeader>
              <CardContent>
                {generatedLineup.length > 0 ? (
                  <PlayersOrderedList
                    players={generatedLineup}
                    onItemClick={(p) =>
                      setSelected(players.find((x) => x.id === p.id) ?? null)
                    }
                    badgeClassName="bg-primary text-white dark:bg-primary"
                  />
                ) : (
                  <div className="text-center text-muted-foreground py-8">
                    Use the generator to get a preview here.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* ANALYSIS */}
        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Lineup Analysis</CardTitle>
              <CardDescription>
                Statistical breakdown and insights
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center text-muted-foreground py-8">
                Generate a lineup first to see detailed analysis and
                recommendations
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// also export as default for existing default imports
export default LineupOptimizer;

// Minimal lineup generation tester
export function LineupGeneratorTester() {
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setGenerating(true);
    setError(null);
    setResult(null);
    try {
      // Minimal payload - backend expects only team_id
      const payload = { team_id: 1 };
      const res = await fetch(`${API_BASE}/lineups/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err?.message ?? String(err));
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="p-4 border-t mt-4">
      <h3 className="text-lg font-medium mb-2">Lineup generation tester</h3>
      <p className="text-sm text-gray-600 mb-2">
        Click to request the backend to generate a lineup and return the
        players.
      </p>
      <div className="flex items-center gap-2">
        <button
          className="px-3 py-1 bg-primary text-white rounded disabled:opacity-50"
          onClick={generate}
          disabled={generating}
        >
          {generating ? "Generating…" : "Generate Lineup (POST)"}
        </button>
        {error && <div className="text-red-600">Error: {error}</div>}
      </div>

      {result && (
        <div className="mt-3">
          <div className="mb-1">Response preview:</div>
          <pre className="text-xs max-h-64 overflow-auto border p-2 bg-gray-50">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
