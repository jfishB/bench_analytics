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
import * as lineupService from "../../features/lineup/services/lineupService";
import { DragEndEvent } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import { ManualModePanel } from "../../features/lineup/components/ManualModePanel";
import { SabermetricsModePanel } from "../../features/lineup/components/SabermetricsModePanel";
import { LineupSimulatorTab } from "../../features/lineup/components/LineupSimulatorTab";
import { Alert, AlertDescription, AlertTitle } from "../../ui/components/alert";
import { Player } from "../../shared/types";

// Simple debugging page: fetch roster players and display basic status

// Main page: tabs with Roster, Optimizer (generate) and Analysis
export function LineupOptimizer() {
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<Player[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Player | null>(null);

  // Player selection state
  const [selectedPlayerIds, setSelectedPlayerIds] = useState<Set<number>>(
    new Set()
  );
  const [selectionWarning, setSelectionWarning] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("current");
  const [lineupCreated, setLineupCreated] = useState<boolean>(false);
  const [lineupMode, setLineupMode] = useState<"manual" | "sabermetrics">(
    "manual"
  );

  // lineup generation states
  const [lineupPlayers, setLineupPlayers] = useState<Player[]>([]);
  const [battingOrderLineup, setBattingOrderLineup] = useState<Player[]>([]);
  const [generatedLineup, setGeneratedLineup] = useState<Player[]>([]);
  const [generating, setGenerating] = useState(false);
  const [teamId, setTeamId] = useState<number | undefined>(1);

  // Separate lineup name and save status for each mode
  const [manualLineupName, setManualLineupName] = useState<string>("");
  const [manualSaveStatus, setManualSaveStatus] = useState<
    "idle" | "saving" | "saved"
  >("idle");

  const [sabermetricsLineupName, setSabermetricsLineupName] =
    useState<string>("");
  const [sabermetricsSaveStatus, setSabermetricsSaveStatus] = useState<
    "idle" | "saving" | "saved"
  >("idle");

  // Saved lineups (for Lineup Simulator tab)
  const [savedLineups, setSavedLineups] = useState<lineupService.SavedLineup[]>(
    []
  );
  const [loadingLineups, setLoadingLineups] = useState(false);

  // Handle drag end for batting order
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setBattingOrderLineup((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);

        const newOrder = arrayMove(items, oldIndex, newIndex);
        // Update batting orders
        return newOrder.map((player, index) => ({
          ...player,
          batting_order: index + 1,
        }));
      });
    }
  };

  // Generic save handler for both modes
  const saveLineup = async (
    name: string,
    players: Player[],
    setSaveStatus: React.Dispatch<
      React.SetStateAction<"idle" | "saving" | "saved">
    >,
    clearName: () => void
  ) => {
    setSaveStatus("saving");
    try {
      const payload: lineupService.SaveLineupPayload = {
        team_id: teamId!,
        name,
        players: players.map((p) => ({
          player_id: p.id,
          position: p.position || "DH",
          batting_order: p.batting_order!,
        })),
      };

      await lineupService.saveLineup(payload);

      setSaveStatus("saved");
      fetchSavedLineups(); // Refresh lineup list
      setTimeout(() => {
        setSaveStatus("idle");
        clearName(); // Clear the name field for next lineup
      }, 1000);
    } catch (err: any) {
      console.error("Failed to save lineup:", err);
      setError(err?.message || "Failed to save lineup");
      setSaveStatus("idle");
    }
  };

  // Handle save for manual mode
  const handleManualSave = async () => {
    await saveLineup(
      manualLineupName,
      battingOrderLineup,
      setManualSaveStatus,
      () => setManualLineupName("")
    );
  };

  // Handle generate for sabermetrics mode
  const handleSabermetricsGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const data = await lineupService.generateLineup(teamId!);
      const ordered = (data.players || []).map((p: any) => {
        const full = players.find((r) => r.id === p.player_id) || {
          id: p.player_id,
          name: p.player_name ?? "Unknown",
          position: p.position,
          team: String(p.team ?? teamId),
        };
        return {
          ...full,
          batting_order: p.batting_order,
        };
      });
      setGeneratedLineup(ordered);
    } catch (err: any) {
      console.error("Generation failed:", err);
      setError(err?.message || "Failed to generate");
    } finally {
      setGenerating(false);
    }
  };

  // Handle save for sabermetrics mode
  const handleSabermetricsSave = async () => {
    await saveLineup(
      sabermetricsLineupName,
      generatedLineup,
      setSabermetricsSaveStatus,
      () => setSabermetricsLineupName("")
    );
  };

  // Toggle player selection
  const togglePlayerSelection = (player: Player) => {
    const playerId = player.id;
    setSelectedPlayerIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(playerId)) {
        newSet.delete(playerId);
        setSelectionWarning(null); // Clear warning when deselecting
        setLineupCreated(false); // Reset lineup when changing selection
      } else {
        if (newSet.size >= 9) {
          setSelectionWarning(
            "A maximum of 9 players can be selected for a lineup!"
          );
          setTimeout(() => setSelectionWarning(null), 4000); // Auto-dismiss after 4 seconds
          return prev;
        }
        newSet.add(playerId);
        setLineupCreated(false); // Reset lineup when changing selection
      }
      return newSet;
    });
  };

  // Fetch saved lineups
  const fetchSavedLineups = async () => {
    setLoadingLineups(true);
    try {
      const data = await lineupService.fetchSavedLineups();
      setSavedLineups(data);
    } catch (err: any) {
      console.error("Failed to fetch lineups:", err);
    } finally {
      setLoadingLineups(false);
    }
  };

  // Fetch saved lineups when switching to analysis tab
  useEffect(() => {
    if (activeTab === "analysis") {
      fetchSavedLineups();
    }
  }, [activeTab]);

  useEffect(() => {
    let cancelled = false;
    async function loadPlayers() {
      setLoading(true);
      setError(null);
      try {
        const raw = await lineupService.fetchPlayers(teamId);
        if (!cancelled) {
          setPlayers(raw);
          // initialize lineupPlayers to the roster mapping shape the list expects
          setLineupPlayers(raw);
          // detect team id if available
          if (raw.length > 0) {
            const first = raw[0];
            if (first.team && typeof first.team === "string") {
              const parsedTeamId = parseInt(first.team, 10);
              if (!isNaN(parsedTeamId)) setTeamId(parsedTeamId);
            }
          }
        }
      } catch (err: any) {
        if (!cancelled) setError(err?.message ?? String(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadPlayers();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

      {/* Global Error Display */}
      {error && (
        <Alert variant="error" onClose={() => setError(null)}>
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="current">Current Roster</TabsTrigger>
          <TabsTrigger value="optimizer">Generate Lineup</TabsTrigger>
          <TabsTrigger value="analysis">Lineup Simulator</TabsTrigger>
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
              {/* Selection Warning Banner */}
              {selectionWarning && (
                <div className="mb-4">
                  <Alert variant="warning" onClose={() => setSelectionWarning(null)}>
                    <AlertDescription>{selectionWarning}</AlertDescription>
                  </Alert>
                </div>
              )}

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
                      <div className="overflow-y-auto max-h-[350px]">
                        <PlayersOrderedList
                          players={players.map((p) => ({
                            id: p.id,
                            name: p.name,
                            position: p.position,
                            team: String(p.team),
                            batting_order: p.batting_order,
                            isSelected: selectedPlayerIds.has(p.id),
                          }))}
                          onItemClick={(p) =>
                            setSelected(
                              players.find((x) => x.id === p.id) ?? null
                            )
                          }
                          onSelectionToggle={togglePlayerSelection}
                          showCheckboxes={true}
                        />
                      </div>
                    </>
                  )}
                </div>

                <div className="h-full flex flex-col">
                  {/* Selection count and Create Lineup button - Always visible */}
                  <div className="mb-4 p-3 bg-white border rounded">
                    <div
                      className={`text-sm font-medium mb-3 ${
                        selectedPlayerIds.size === 9
                          ? "text-green-700"
                          : "text-gray-700"
                      }`}
                    >
                      Batters selected: {selectedPlayerIds.size}/9
                    </div>
                    <Button
                      className="w-full disabled:bg-gray-200 disabled:cursor-not-allowed"
                      disabled={selectedPlayerIds.size !== 9}
                      onClick={() => {
                        // Get selected players from the players array
                        const selectedPlayers = players
                          .filter((p) => selectedPlayerIds.has(p.id))
                          .map((p, index) => ({
                            ...p,
                            batting_order: index + 1, // Assign batting order 1-9
                          }));

                        setLineupPlayers(selectedPlayers);
                        setBattingOrderLineup(selectedPlayers); // Initialize batting order
                        setLineupCreated(true); // Mark lineup as created
                        setActiveTab("optimizer"); // Switch to Generate Lineup tab
                      }}
                    >
                      Create Lineup
                    </Button>
                  </div>

                  {/* Player details card */}
                  {selected ? (
                    <div className="w-full">
                      <PlayerCard
                        id={selected.id}
                        name={selected.name}
                        teamID={String(selected.team)}
                        className="w-full"
                      />

                      <div className="mt-3 bg-gray-50 border rounded p-3 text-sm">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <div className="text-xs text-gray-500">PA</div>
                            <div className="font-medium">
                              {selected.pa ?? "—"}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">OBP</div>
                            <div className="font-medium">
                              {selected.on_base_percent ?? "—"}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Hits</div>
                            <div className="font-medium">
                              {selected.hit ?? "—"}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">
                              Walks
                            </div>
                            <div className="font-medium">
                              {selected.walk ?? "—"}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 italic py-6">
                      Click on a player to view details.
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* LINEUP OPTIMIZER */}
        <TabsContent value="optimizer" className="space-y-4">
          {!lineupCreated ? (
            <Card>
              <CardHeader>
                <CardTitle>Lineup Optimizer</CardTitle>
                <CardDescription>
                  Select 9 players to create your lineup
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <svg
                    className="h-16 w-16 text-gray-400 mb-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Select 9 Players From Your Roster First
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Go to the Current Roster tab, select 9 players using the
                    checkboxes, then click "Create Lineup".
                  </p>
                  <p className="text-sm font-medium text-gray-700">
                    Currently selected: {selectedPlayerIds.size}/9 players
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Mode Toggle */}
              <div className="mb-6">
                <Tabs
                  value={lineupMode}
                  onValueChange={(value) =>
                    setLineupMode(value as "manual" | "sabermetrics")
                  }
                  className="w-full"
                >
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="manual">Manual</TabsTrigger>
                    <TabsTrigger value="sabermetrics">Sabermetrics</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Manual Mode */}
              {lineupMode === "manual" ? (
                <ManualModePanel
                  lineupPlayers={lineupPlayers}
                  battingOrderLineup={battingOrderLineup}
                  lineupName={manualLineupName}
                  saveStatus={manualSaveStatus}
                  onPlayerClick={(p) =>
                    setSelected(players.find((x) => x.id === p.id) ?? null)
                  }
                  onLineupNameChange={setManualLineupName}
                  onDragEnd={handleDragEnd}
                  onSave={handleManualSave}
                />
              ) : (
                /* Sabermetrics Mode */
                <SabermetricsModePanel
                  lineupPlayers={lineupPlayers}
                  generatedLineup={generatedLineup}
                  lineupName={sabermetricsLineupName}
                  saveStatus={sabermetricsSaveStatus}
                  generating={generating}
                  onPlayerClick={(p) =>
                    setSelected(players.find((x) => x.id === p.id) ?? null)
                  }
                  onLineupNameChange={setSabermetricsLineupName}
                  onGenerate={handleSabermetricsGenerate}
                  onSave={handleSabermetricsSave}
                />
              )}
            </>
          )}
        </TabsContent>

        {/* LINEUP SIMULATOR */}
        <TabsContent value="analysis" className="space-y-4">
          <LineupSimulatorTab
            savedLineups={savedLineups}
            loading={loadingLineups}
          />
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
      // Use lineup service to generate
      const data = await lineupService.generateLineup(1);
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
