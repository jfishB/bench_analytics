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
import { ManualModePanel } from "../../features/lineup/components/ManualModePanel";
import { SabermetricsModePanel } from "../../features/lineup/components/SabermetricsModePanel";
import { LineupSimulatorTab } from "../../features/lineup/components/LineupSimulatorTab";
import { Alert, AlertDescription, AlertTitle } from "../../ui/components/alert";
import { Users, Target, Zap, BarChart3 } from "lucide-react";

// Custom hooks following clean architecture
import { useRosterData } from "../../features/lineup/hooks/useRosterData";
import { usePlayerSelection } from "../../features/lineup/hooks/usePlayerSelection";
import { useLineupCreation } from "../../features/lineup/hooks/useLineupCreation";
import { useManualLineup } from "../../features/lineup/hooks/useManualLineup";
import { useSabermetricsLineup } from "../../features/lineup/hooks/useSabermetricsLineup";
import { useSavedLineups } from "../../features/lineup/hooks/useSavedLineups";

/**
 * LineupOptimizer - Main page component for lineup optimization
 * Refactored to use custom hooks for clean architecture and better state management
 */
export function LineupOptimizer() {
  // UI state (presentation layer) — restore persisted tab on reload
  const [activeTab, setActiveTab] = useState<string>(() => {
    try {
      let storedTab = localStorage.getItem("lineup.activeTab");
      // Migration: "analysis" tab was renamed to "simulation"
      if (storedTab === "analysis") {
        storedTab = "simulation";
        localStorage.setItem("lineup.activeTab", storedTab);
      }
      // Default to "simulation" if no tab is stored (show saved lineups first)
      return storedTab || "simulation";
    } catch {
      return "simulation";
    }
  });

  // Persist active tab so a page reload keeps the same tab
  useEffect(() => {
    try {
      localStorage.setItem("lineup.activeTab", activeTab);
    } catch {
      /* Ignore storage errors (e.g. privacy mode) */
    }
  }, [activeTab]);

  // Custom hooks (domain/business logic layer)
  const { loading, players, error, setError, teamId } = useRosterData();

  const {
    selectedPlayerIds,
    selectionWarning,
    setSelectionWarning,
    togglePlayerSelection,
  } = usePlayerSelection();

  const {
    lineupCreated,
    setLineupCreated,
    lineupPlayers,
    setLineupPlayers,
    selected,
    setSelected,
    createLineup,
  } = useLineupCreation();

  const { savedLineups, loadingLineups, fetchSavedLineups } = useSavedLineups();

  // Manual lineup hook with save callback
  const {
    battingOrderLineup,
    setBattingOrderLineup,
    manualLineupName,
    setManualLineupName,
    manualSaveStatus,
    handleDragEnd,
    saveLineup: saveManualLineup,
  } = useManualLineup(teamId, fetchSavedLineups);

  // Sabermetrics lineup hook with save callback
  const {
    generatedLineup,
    generating,
    sabermetricsLineupName,
    setSabermetricsLineupName,
    sabermetricsSaveStatus,
    generateLineup: generateSabermetricsLineup,
    saveLineup: saveSabermetricsLineup,
  } = useSabermetricsLineup(teamId, players, fetchSavedLineups);

  // Initialize lineupPlayers when roster loads
  useEffect(() => {
    if (players.length > 0) {
      setLineupPlayers(players);
    }
  }, [players, setLineupPlayers]);

  // Fetch saved lineups when switching to simulation tab
  useEffect(() => {
    if (activeTab === "simulation") {
      fetchSavedLineups();
    }
  }, [activeTab, fetchSavedLineups]);

  // Handle player selection with lineup reset
  const handleTogglePlayerSelection = (player: any) => {
    togglePlayerSelection(player, () => setLineupCreated(false));
  };

  // Handle create lineup button
  const handleCreateLineup = () => {
    const selectedPlayers = players.filter((p) => selectedPlayerIds.has(p.id));
    const lineup = createLineup(selectedPlayers);
    setBattingOrderLineup(lineup);
    setActiveTab("optimizer");
  };

  // Wrapper handlers for save operations with error handling
  const handleManualSave = async () => {
    try {
      await saveManualLineup();
    } catch (err: any) {
      setError(err?.message || "Failed to save lineup");
    }
  };

  const handleSabermetricsGenerate = async () => {
    try {
      setError(null);
      // Pass selected player ids to the generator so the backend can
      // suggest a lineup constrained to the current selection.
      const selectedIdsArr = Array.from(selectedPlayerIds);
      await generateSabermetricsLineup(selectedIdsArr);
    } catch (err: any) {
      setError(err?.message || "Failed to generate lineup");
    }
  };

  const handleSabermetricsSave = async () => {
    try {
      await saveSabermetricsLineup();
    } catch (err: any) {
      setError(err?.message || "Failed to save lineup");
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center">
        <h1 className="text-3xl mb-2 text-primary">Lineup Optimizer</h1>
        <p className="text-muted-foreground">
          Generate optimal batting orders based on player statistics
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
        <TabsList className="grid w-full grid-cols-4 h-auto p-1 bg-gradient-to-r from-blue-50 to-red-50">
          <TabsTrigger
            value="current"
            className="gap-2 data-[state=active]:bg-white data-[state=active]:shadow-md"
            aria-label="Roster"
          >
            <Users className="h-4 w-4" />
            <span className="hidden sm:inline">Roster</span>
          </TabsTrigger>
          <TabsTrigger
            value="manual"
            className="gap-2 data-[state=active]:bg-white data-[state=active]:shadow-md"
            aria-label="Builder"
          >
            <Target className="h-4 w-4" />
            <span className="hidden sm:inline">Builder</span>
          </TabsTrigger>
          <TabsTrigger
            value="optimizer"
            className="gap-2 data-[state=active]:bg-white data-[state=active]:shadow-md"
            aria-label="Generate"
          >
            <Zap className="h-4 w-4" />
            <span className="hidden sm:inline">Generate</span>
          </TabsTrigger>
          <TabsTrigger
            value="simulation"
            className="gap-2 data-[state=active]:bg-white data-[state=active]:shadow-md"
            aria-label="Simulate"
          >
            <BarChart3 className="h-4 w-4" />
            <span className="hidden sm:inline">Simulate</span>
          </TabsTrigger>
        </TabsList>

        {/* CURRENT ROSTER */}
        <TabsContent value="current" className="space-y-4">
          <Card className="border-0 shadow-lg bg-gradient-to-br from-white to-blue-50/30">
            <CardHeader>
              <div className="flex items-center gap-2">
                <div className="p-2 bg-blue-900/10 rounded-lg">
                  <Users className="h-5 w-5 text-blue-900" />
                </div>
                <div>
                  <CardTitle>Available Players</CardTitle>
                  <CardDescription>
                    Click to add players to your lineup
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Selection Warning Banner */}
              {selectionWarning && (
                <div className="mb-4">
                  <Alert
                    variant="warning"
                    onClose={() => setSelectionWarning(null)}
                  >
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
                            team: String(p.team),
                            batting_order: p.batting_order,
                            isSelected: selectedPlayerIds.has(p.id),
                          }))}
                          onItemClick={(p) =>
                            setSelected(
                              players.find((x) => x.id === p.id) ?? null
                            )
                          }
                          onSelectionToggle={handleTogglePlayerSelection}
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
                      onClick={handleCreateLineup}
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
                            <div className="text-xs text-gray-500">Walks</div>
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

        {/* LINEUP OPTIMIZER - SABERMETRICS */}
        <TabsContent value="optimizer" className="space-y-4">
          {!lineupCreated ? (
            <Card>
              <CardHeader>
                <CardTitle>Generate Lineup (Sabermetrics)</CardTitle>
                <CardDescription>
                  Select 9 players to create an optimized lineup
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
        </TabsContent>

        {/* LINEUP BUILDER - MANUAL */}
        <TabsContent value="manual" className="space-y-4">
          {!lineupCreated ? (
            <Card>
              <CardHeader>
                <CardTitle>Build Lineup (Manual)</CardTitle>
                <CardDescription>
                  Select 9 players to create a custom lineup
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
          )}
        </TabsContent>

        {/* LINEUP SIMULATOR */}
        <TabsContent value="simulation" className="space-y-4">
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
