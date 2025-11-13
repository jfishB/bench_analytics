import { useState } from "react";
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

export function LineupOptimizer() {
  const samplePlayers: Player[] = [
    {
      id: 1,
      name: "Mike Rodriguez",
      position: "C",
      avg: 0.285,
      obp: 0.342,
      ops: 0.798,
      batting_order: 1,
      team: "Aces",
    },
    {
      id: 2,
      name: "Tommy Chen",
      position: "1B",
      avg: 0.312,
      obp: 0.378,
      ops: 0.889,
      batting_order: 5,
      team: "Aces",
    },
    {
      id: 3,
      name: "Jake Williams",
      position: "2B",
      avg: 0.267,
      obp: 0.321,
      ops: 0.745,
      batting_order: 8,
      team: "Aces",
    },
    {
      id: 4,
      name: "Carlos Martinez",
      position: "3B",
      avg: 0.298,
      obp: 0.365,
      ops: 0.834,
      batting_order: 4,
      team: "Aces",
    },
    {
      id: 5,
      name: "David Johnson",
      position: "SS",
      avg: 0.275,
      obp: 0.338,
      ops: 0.772,
      batting_order: 6,
      team: "Aces",
    },
    {
      id: 6,
      name: "Alex Thompson",
      position: "LF",
      avg: 0.289,
      obp: 0.351,
      ops: 0.812,
      batting_order: 7,
      team: "Aces",
    },
    {
      id: 7,
      name: "Ryan Davis",
      position: "CF",
      avg: 0.304,
      obp: 0.372,
      ops: 0.867,
      batting_order: 3,
      team: "Aces",
    },
    {
      id: 8,
      name: "Josh Miller",
      position: "RF",
      avg: 0.281,
      obp: 0.329,
      ops: 0.786,
      batting_order: 9,
      team: "Aces",
    },
    {
      id: 9,
      name: "Sam Wilson",
      position: "DH",
      avg: 0.325,
      obp: 0.391,
      ops: 0.923,
      batting_order: 2,
      team: "Aces",
    },
  ];

  const [rosterPlayers] = useState<Player[]>(samplePlayers);
  const [lineupPlayers] = useState<Player[]>(samplePlayers);
  const [generatedLineup, setGeneratedLineup] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = () => {
    setGenerating(true);
    const source = lineupPlayers.length ? lineupPlayers : rosterPlayers;
    const newLineup = generateLineup(source);
    setGeneratedLineup(newLineup);
    setGenerating(false);
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
                <PlayersOrderedList
                  players={rosterPlayers}
                  onItemClick={(p) => setSelectedPlayer(p)}
                />
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
                    disabled={generating}
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
