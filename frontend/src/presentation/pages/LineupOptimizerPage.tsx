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
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import PlayerList from "../../ui/components/player-list";

// Sortable player item component for drag and drop
interface SortablePlayerItemProps {
  player: any;
  index: number;
}

function SortablePlayerItem({ player, index }: SortablePlayerItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: player.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="flex items-center bg-white border border-gray-200 rounded-lg p-3 shadow-sm cursor-move hover:bg-gray-50"
    >
      <div className="w-10 flex-shrink-0">
        <div className="h-8 w-8 rounded-full flex items-center justify-center font-semibold bg-primary text-white">
          {player.batting_order || index + 1}
        </div>
      </div>
      <div className="ml-3 flex-1">
        <div className="text-sm font-medium text-gray-900">{player.name}</div>
        <div className="text-xs text-gray-500">{player.position || "—"}</div>
      </div>
      <div className="ml-3">
        <svg
          className="h-5 w-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 8h16M4 16h16"
          />
        </svg>
      </div>
    </div>
  );
}

// Simple debugging page: fetch roster players and display basic status

// Main page: tabs with Roster, Optimizer (generate) and Analysis
export function LineupOptimizer() {
  const [loading, setLoading] = useState(true);
  const [players, setPlayers] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<any | null>(null);

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
  const [lineupPlayers, setLineupPlayers] = useState<any[]>([]);
  const [battingOrderLineup, setBattingOrderLineup] = useState<any[]>([]);
  const [generatedLineup, setGeneratedLineup] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [teamId, setTeamId] = useState<number | undefined>(1);

  // Lineup name and save status
  const [lineupName, setLineupName] = useState<string>("");
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved">(
    "idle"
  );

  // Saved lineups (for Lineup Simulator tab)
  const [savedLineups, setSavedLineups] = useState<any[]>([]);
  const [loadingLineups, setLoadingLineups] = useState(false);

  // Drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

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

  // Toggle player selection
  const togglePlayerSelection = (player: any) => {
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
                <div className="mb-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-r flex items-center justify-between">
                  <div className="flex items-center">
                    <svg
                      className="h-5 w-5 text-yellow-400 mr-3"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <p className="text-sm font-medium text-yellow-800">
                      {selectionWarning}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectionWarning(null)}
                    className="text-yellow-600 hover:text-yellow-800 font-bold"
                  >
                    ✕
                  </button>
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
                <div className="grid md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Selected Players</CardTitle>
                      <CardDescription>
                        Your 9 selected players - drag them to arrange batting
                        order
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <PlayersOrderedList
                        players={lineupPlayers}
                        onItemClick={(p) =>
                          setSelected(
                            players.find((x) => x.id === p.id) ?? null
                          )
                        }
                        badgeClassName="bg-gray-400 text-white"
                      />
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Batting Order</CardTitle>
                      <CardDescription>
                        Drag players to rearrange the batting order
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <DndContext
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                      >
                        <SortableContext
                          items={battingOrderLineup.map((p) => p.id)}
                          strategy={verticalListSortingStrategy}
                        >
                          <div className="space-y-2">
                            {battingOrderLineup.map((player, index) => (
                              <SortablePlayerItem
                                key={player.id}
                                player={player}
                                index={index}
                              />
                            ))}
                          </div>
                        </SortableContext>
                      </DndContext>

                      <div className="mt-6 space-y-3">
                        <div>
                          <label
                            htmlFor="lineup-name-manual"
                            className="block text-sm font-medium text-gray-700 mb-1"
                          >
                            Lineup Name
                          </label>
                          <input
                            id="lineup-name-manual"
                            type="text"
                            value={lineupName}
                            onChange={(e) => setLineupName(e.target.value)}
                            placeholder="Enter lineup name..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                          />
                        </div>
                        <Button
                          className={`w-full ${
                            saveStatus === "saved"
                              ? "bg-green-600 hover:bg-green-600"
                              : ""
                          } disabled:bg-gray-200 disabled:cursor-not-allowed`}
                          disabled={
                            !lineupName.trim() || saveStatus === "saving"
                          }
                          onClick={async () => {
                            setSaveStatus("saving");
                            try {
                              const payload: lineupService.SaveLineupPayload = {
                                team_id: teamId!,
                                name: lineupName,
                                players: battingOrderLineup.map((p) => ({
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
                                setLineupName(""); // Clear the name field for next lineup
                              }, 1000);
                            } catch (err: any) {
                              console.error("Failed to save lineup:", err);
                              setError(err?.message || "Failed to save lineup");
                              setSaveStatus("idle");
                            }
                          }}
                        >
                          {saveStatus === "saving"
                            ? "Saving..."
                            : saveStatus === "saved"
                            ? "Saved ✓"
                            : "Save Lineup"}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                /* Sabermetrics Mode */
                <div className="grid md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Algorithm Generator</CardTitle>
                      <CardDescription>
                        Generate an optimal batting order using sabermetrics
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-sm text-muted-foreground mb-4">
                        Use the algorithm to generate an optimal lineup based on
                        player statistics.
                      </div>
                      <div className="pt-4">
                        <PlayersOrderedList
                          players={lineupPlayers}
                          onItemClick={(p) =>
                            setSelected(
                              players.find((x) => x.id === p.id) ?? null
                            )
                          }
                          badgeClassName="bg-gray-400 text-white"
                        />
                        <div className="pt-4">
                          <Button
                            className="w-full"
                            onClick={async () => {
                              setGenerating(true);
                              setError(null);
                              try {
                                const data = await lineupService.generateLineup(teamId!);
                                const ordered = (data.players || []).map(
                                  (p: any) => {
                                    const full = players.find(
                                      (r) => r.id === p.player_id
                                    ) || {
                                      id: p.player_id,
                                      name: p.player_name ?? "Unknown",
                                      position: p.position,
                                      team: String(p.team ?? teamId),
                                    };
                                    return {
                                      ...full,
                                      batting_order: p.batting_order,
                                    };
                                  }
                                );
                                setGeneratedLineup(ordered);
                              } catch (err: any) {
                                console.error("Generation failed:", err);
                                setError(err?.message || "Failed to generate");
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
                        Optimal batting order generated by the algorithm
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {generatedLineup.length > 0 ? (
                        <>
                          <PlayersOrderedList
                            players={generatedLineup}
                            onItemClick={(p) =>
                              setSelected(
                                players.find((x) => x.id === p.id) ?? null
                              )
                            }
                            badgeClassName="bg-primary text-white dark:bg-primary"
                          />
                          <div className="mt-6 space-y-3">
                            <div>
                              <label
                                htmlFor="lineup-name-sabermetrics"
                                className="block text-sm font-medium text-gray-700 mb-1"
                              >
                                Lineup Name
                              </label>
                              <input
                                id="lineup-name-sabermetrics"
                                type="text"
                                value={lineupName}
                                onChange={(e) => setLineupName(e.target.value)}
                                placeholder="Enter lineup name..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                              />
                            </div>
                            <Button
                              className={`w-full ${
                                saveStatus === "saved"
                                  ? "bg-green-600 hover:bg-green-600"
                                  : ""
                              } disabled:bg-gray-200 disabled:cursor-not-allowed`}
                              disabled={
                                !lineupName.trim() || saveStatus === "saving"
                              }
                              onClick={async () => {
                                setSaveStatus("saving");
                                try {
                                  const payload: lineupService.SaveLineupPayload = {
                                    team_id: teamId!,
                                    name: lineupName,
                                    players: generatedLineup.map((p) => ({
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
                                    setLineupName(""); // Clear the name field for next lineup
                                  }, 1000);
                                } catch (err: any) {
                                  console.error("Failed to save lineup:", err);
                                  setError(
                                    err?.message || "Failed to save lineup"
                                  );
                                  setSaveStatus("idle");
                                }
                              }}
                            >
                              {saveStatus === "saving"
                                ? "Saving..."
                                : saveStatus === "saved"
                                ? "Saved ✓"
                                : "Save Lineup"}
                            </Button>
                          </div>
                        </>
                      ) : (
                        <div className="text-center text-muted-foreground py-8">
                          Click "Generate Lineup" to see the optimal batting
                          order.
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              )}
            </>
          )}
        </TabsContent>

        {/* LINEUP SIMULATOR */}
        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Lineup Simulator</CardTitle>
              <CardDescription>
                View and simulate all your saved lineups
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingLineups ? (
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
                    Create and save lineups in the Generate Lineup tab to see
                    them here.
                  </p>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {savedLineups.map((lineup: any) => (
                    <Card
                      key={lineup.id}
                      className="hover:shadow-lg transition-shadow"
                    >
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">{lineup.name}</CardTitle>
                        <CardDescription className="text-xs">
                          Created:{" "}
                          {new Date(lineup.created_at).toLocaleDateString()}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="text-sm font-medium text-gray-700 mb-2">
                            Batting Order:
                          </div>
                          <div className="space-y-1">
                            {lineup.players
                              ?.sort(
                                (a: any, b: any) =>
                                  a.batting_order - b.batting_order
                              )
                              .map((player: any) => (
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
                                  <span className="text-xs text-gray-500">
                                    {player.position}
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
