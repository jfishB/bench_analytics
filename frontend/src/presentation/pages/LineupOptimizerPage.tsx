import { useEffect, useRef, useState } from "react";
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
import { generateLineup } from "../../features/lineup/usecases/lineupOptimizerUseCase";
import { Player } from "../../shared/types";

// TODO: check if clean architecture is mantained here?
// Convert roster API player objects into the frontend Player shape.
function mapRosterApiPlayers(apiPlayers: any[]): Player[] {
  return apiPlayers.map((p) => ({
    id: Number(p.id),
    name: p.name ?? "Unnamed",
    // many roster endpoints may not include `position` or `team` in the minimal view
    position: (p.position as string) ?? "--",
    // normalize team: could be numeric id, object {id,name} or team_name string
    team:
      typeof p.team === "number"
        ? String(p.team)
        : p.team && typeof p.team === "object"
        ? p.team.name ?? String(p.team.id ?? "")
        : (p.team_name as string) ?? (p.team_id ? String(p.team_id) : ""),
    avg: (p.avg as number) ?? undefined,
    obp: (p.obp as number) ?? undefined,
    ops: (p.ops as number) ?? undefined,
    batting_order: (p.batting_order as number) ?? undefined,
  }));
}


/**
 * Small presentational helper that accepts raw roster API payload and
 * returns a PlayersOrderedList for display. Keeps mapping logic centralized
 * so the rest of the page can remain simple.
 */
export function RosterApiDisplay({
  apiData,
  onItemClick,
  badgeClassName,
}: {
  apiData: any;
  onItemClick?: (p: Player) => void;
  badgeClassName?: string;
}) {
  const players = Array.isArray(apiData?.players) ? mapRosterApiPlayers(apiData.players) : [];

  return (
    <PlayersOrderedList
      players={players}
      onItemClick={onItemClick}
      badgeClassName={badgeClassName}
    />
  );
}

export function LineupOptimizer() {
  // Load roster from the backend and use it as the source of truth
  const [rosterPlayers, setRosterPlayers] = useState<Player[]>([]);
  const [lineupPlayers, setLineupPlayers] = useState<Player[]>([]);
  const [generatedLineup, setGeneratedLineup] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [generating, setGenerating] = useState(false);
  const [loadingRoster, setLoadingRoster] = useState(false);
  const [rosterError, setRosterError] = useState<string | null>(null);
  const [teamId, setTeamId] = useState<number | undefined>(undefined);

  const isMountedRef = useRef(true);

  const fetchRoster = async () => {
    setLoadingRoster(true);
    setRosterError(null);
    try {
      const res = await fetch("/api/v1/roster/players/");
      if (!res.ok) throw new Error(`Failed to load roster: ${res.status}`);
  const data = await res.json();
  // Support multiple possible shapes: array, {players: []}, {results: []}
  let rawPlayers: any[] = [];
  if (Array.isArray(data)) rawPlayers = data;
  else if (Array.isArray(data.players)) rawPlayers = data.players;
  else if (Array.isArray(data.results)) rawPlayers = data.results;
  else rawPlayers = [];
  // debug visibility when roster doesn't load
  console.debug("fetchRoster: received data shape", { data, rawPlayersLength: rawPlayers.length });

      // determine team id if present on payload
      const first = rawPlayers[0];
      let detectedTeamId: number | undefined = undefined;
      if (first) {
        if (typeof first.team === "number") detectedTeamId = first.team;
        else if (first.team && typeof first.team === "object" && first.team.id) detectedTeamId = first.team.id;
        else if (typeof first.team_id === "number") detectedTeamId = first.team_id;
      }

      const mapped = mapRosterApiPlayers(rawPlayers);
  console.debug("fetchRoster: mapped players", mapped.length, mapped.slice(0,3));
      if (!isMountedRef.current) return;
      setRosterPlayers(mapped);
      setLineupPlayers(mapped);
      if (mapped.length === 0) {
        setRosterError("No players returned from roster API");
      }
      setTeamId(detectedTeamId);
    } catch (err: any) {
      console.error("Failed to load roster", err);
      if (isMountedRef.current) setRosterError(err?.message ?? String(err));
    } finally {
      if (isMountedRef.current) setLoadingRoster(false);
    }
  };

  useEffect(() => {
    fetchRoster();
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    const payload = {
      team_id: teamId ?? rosterPlayers[0]?.team ?? 1,
      name: "Auto-generated lineup",
      opponent_pitcher_id: null,
      opponent_team_id: null,
    };
    try {

      const res = await fetch("/api/v1/lineups/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    // API returns players 
    const ordered = (data.players || [])
      .slice()
      .map((p: any) => {
        // Try to find the full Player object in rosterPlayers or lineupPlayers
        const full =
          rosterPlayers.find((r) => r.id === p.player_id) ||
          lineupPlayers.find((r) => r.id === p.player_id) || {
            id: p.player_id,
            name: "Unknown",
            position: p.position,
            team: "",
          };

        return { ...full, batting_order: p.batting_order };
      });

    setGeneratedLineup(ordered);
  } catch (err) {
    console.error("Lineup generation via server failed, falling back to client:", err);
    // Fallback: local heuristic
    const source = lineupPlayers.length ? lineupPlayers : rosterPlayers;
    const newLineup = generateLineup(source);
    setGeneratedLineup(newLineup);
  } finally {
    setGenerating(false);
  }
};

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
                  {rosterError && (
                    <div className="mb-2 text-sm text-red-600">
                      Failed to load roster: {rosterError} <Button onClick={() => fetchRoster()}>Retry</Button>
                    </div>
                  )}

                  <div className="relative">
                    {loadingRoster && rosterPlayers.length === 0 ? (
                      <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/60">
                        <div className="text-sm">Loading roster…</div>
                      </div>
                    ) : loadingRoster ? (
                      <div className="absolute top-2 right-2 z-10 text-xs px-2 py-1 bg-white/80 rounded">Refreshing…</div>
                    ) : null}

                    <PlayersOrderedList
                      players={rosterPlayers}
                      onItemClick={(p) => setSelectedPlayer(p)}
                    />
                  </div>
                </div>
                <div className="h-full flex items-start">
                  {selectedPlayer ? (
                    <PlayerCard
                      id={selectedPlayer.id}
                      name={selectedPlayer.name}
                      teamName={selectedPlayer.team}
                      battingPosition={selectedPlayer.position}
                      className="w-full max-h-48 overflow-auto"
                    />
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
                <PlayersOrderedList
                  players={lineupPlayers}
                  onItemClick={(p) => setSelectedPlayer(p)}
                  badgeClassName="bg-primary text-white dark:bg-primary"
                />
                <div className="pt-4">
                  <Button
                    onClick={handleGenerate}
                    className="w-full"
                    disabled={generating || loadingRoster || typeof teamId === "undefined"}
                  >
                    {generating ? "Generating…" : "Generate Lineup"}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Generated Lineup</CardTitle>
                <CardDescription>
                  {generatedLineup.length > 0
                    ? "Optimized batting order"
                    : "Current lineup (not generated)"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {generatedLineup.length > 0 ? (
                  <PlayersOrderedList
                    players={generatedLineup}
                    onItemClick={(p) => setSelectedPlayer(p)}
                    badgeClassName="bg-primary text-white dark:bg-primary"
                  />
                ) : (
                  <div className="text-center text-muted-foreground py-8">
                    No lineup generated yet
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
