import { useState, useEffect } from "react"
import { Button } from "../../ui/components/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/components/card"
import PlayersOrderedList from "../../features/players/components/PlayersOrderedList";
import { PlayerCard } from "../../ui/components/player-card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../ui/components/tabs"

export function LineupOptimizer() {
  // players will be loaded from the backend (expected to include batting_order)
  const samplePlayers = [
    { id: 1, name: "Mike Rodriguez", position: "C", avg: 0.285, obp: 0.342, ops: 0.798, batting_order: 1 },
    { id: 2, name: "Tommy Chen", position: "1B", avg: 0.312, obp: 0.378, ops: 0.889, batting_order: 5 },
    { id: 3, name: "Jake Williams", position: "2B", avg: 0.267, obp: 0.321, ops: 0.745, batting_order: 8 },
    { id: 4, name: "Carlos Martinez", position: "3B", avg: 0.298, obp: 0.365, ops: 0.834, batting_order: 4 },
    { id: 5, name: "David Johnson", position: "SS", avg: 0.275, obp: 0.338, ops: 0.772, batting_order: 6 },
    { id: 6, name: "Alex Thompson", position: "LF", avg: 0.289, obp: 0.351, ops: 0.812, batting_order: 7 },
    { id: 7, name: "Ryan Davis", position: "CF", avg: 0.304, obp: 0.372, ops: 0.867, batting_order: 3 },
    { id: 8, name: "Josh Miller", position: "RF", avg: 0.281, obp: 0.329, ops: 0.786, batting_order: 9 },
    { id: 9, name: "Sam Wilson", position: "DH", avg: 0.325, obp: 0.391, ops: 0.923, batting_order: 2 },
  ]

  const [rosterPlayers, setRosterPlayers] = useState<any[]>(samplePlayers)
  const [lineupPlayers, setLineupPlayers] = useState<any[]>(samplePlayers)
  const [selectedPlayer, setSelectedPlayer] = useState<any | null>(null)
  const [generatedLineup, setGeneratedLineup] = useState<any[]>([])
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [lineupName, setLineupName] = useState<string>("")

  useEffect(() => {
    let cancelled = false

    async function loadRoster() {
      try {
        const res = await fetch("/api/roster")
        if (!res.ok) throw new Error("non-200")
        const data = await res.json()
        if (!cancelled) setRosterPlayers(Array.isArray(data) ? data : samplePlayers)
      } catch (err) {
        if (!cancelled) setRosterPlayers(samplePlayers)
      }
    }

    async function loadLineup() {
      try {
        const res = await fetch("/api/lineup")
        if (!res.ok) throw new Error("non-200")
        const data = await res.json()
        if (!cancelled) setLineupPlayers(Array.isArray(data) ? data : samplePlayers)
      } catch (err) {
        if (!cancelled) setLineupPlayers(samplePlayers)
      }
    }

    loadRoster()
    loadLineup()
    return () => {
      cancelled = true
    }
  }, [])


  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl mb-2 text-primary">Lineup Optimizer</h1>
        <p className="text-muted-foreground">
          Generate optimal batting orders based on player statistics and game situations
        </p>
      </div>

      <Tabs defaultValue="current" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="current">Current Roster</TabsTrigger>
          <TabsTrigger value="optimizer">Generate Lineup</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="current" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Team Roster</CardTitle>
              <CardDescription>Current players and their key statistics</CardDescription>
            </CardHeader>
              <CardContent>
              <div className="grid md:grid-cols-2 gap-4 h-full">
                <div className="h-full">
                  <PlayersOrderedList
                    players={rosterPlayers}
                    onItemClick={(p) => setSelectedPlayer(p)}
                  />
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
                    <div className="text-sm text-gray-500 italic py-6">Select a player to view details.</div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="optimizer" className="space-y-4">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Lineup optimizer</CardTitle>
                <CardDescription>Generate an optimal batting order based on current roster</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <PlayersOrderedList
                    players={lineupPlayers}
                    onItemClick={(p) => setSelectedPlayer(p)}
                    badgeClassName="bg-primary text-white dark:bg-primary"
                  />

                  <div className="pt-4">
                    <Button
                      onClick={async () => {
                        setGenerating(true)
                        try {
                          const res = await fetch("/api/lineup/generate", { method: "POST" })
                          if (!res.ok) throw new Error("Failed to generate lineup")
                          const data = await res.json()
                          // expect backend to return an array of players with batting_order
                          setGeneratedLineup(Array.isArray(data) ? data : [])
                        } catch (err) {
                          console.error(err)
                          // debugging fallback: perform the same client-side heuristic on available data 
                          const source = (lineupPlayers && lineupPlayers.length > 0) ? lineupPlayers : rosterPlayers
                          const sortedByOPS = [...source].sort((a, b) => (b.ops ?? 0) - (a.ops ?? 0))
                          const optimizedOrder = [
                            sortedByOPS.find((p) => (p.obp ?? 0) > 0.35) || sortedByOPS[0],
                            sortedByOPS.find((p) => (p.avg ?? 0) > 0.3 && (p.obp ?? 0) > 0.35) || sortedByOPS[1],
                            sortedByOPS[0],
                            sortedByOPS[1],
                            sortedByOPS[2],
                            ...sortedByOPS.slice(3),
                          ].filter(Boolean).slice(0, 9)
                          setGeneratedLineup(optimizedOrder)
                        } finally {
                          setGenerating(false)
                        }
                      }}
                      className="w-full"
                      disabled={generating}
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
                  {generatedLineup.length > 0 ? "Optimized batting order" : "Current lineup (not generated)"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {generatedLineup.length > 0 ? (
                  <div className="space-y-4">
                    <PlayersOrderedList players={generatedLineup} onItemClick={(p) => setSelectedPlayer(p)} badgeClassName="bg-primary text-white dark:bg-primary" />

                    <div className="pt-2">
                      <div>
                        <label className="text-sm font-medium text-gray-700 mb-1 block">Lineup name</label>
                        <input
                          value={lineupName}
                          onChange={(e) => setLineupName(e.target.value)}
                          placeholder="My optimized lineup"
                          className="w-full px-3 py-2 rounded-md border text-sm bg-white text-gray-900 placeholder:text-gray-400 border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50"
                        />
                      </div>

                      <Button
                        onClick={async () => {
                          setSaving(true)
                          try {
                            const res = await fetch('/api/lineup/save', {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ name: lineupName, lineup: generatedLineup }),
                            })
                            if (!res.ok) throw new Error('Failed to save lineup')
                            setSaveMessage('Lineup saved')
                          } catch (err) {
                            console.error(err)
                            setSaveMessage('Save failed')
                          } finally {
                            setSaving(false)
                            window.setTimeout(() => setSaveMessage(null), 3000)
                          }
                        }}
                        className="w-full"
                        disabled={saving}
                      >
                        {saving ? 'Saving…' : 'Save Lineup'}
                      </Button>

                      {saveMessage ? (
                        <div className="text-sm text-center mt-2 text-muted-foreground">{saveMessage}</div>
                      ) : null}
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground py-8">No lineup generated yet</div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Lineup Analysis</CardTitle>
              <CardDescription>Statistical breakdown and insights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center text-muted-foreground py-8">
                Generate a lineup first to see detailed analysis and recommendations
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
