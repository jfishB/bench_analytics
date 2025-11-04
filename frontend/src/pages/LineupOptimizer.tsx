import * as React from "react";
import { PrettySelect, Label } from "@/components/ui";

type Strategy = "balanced" | "power" | "contact" | "obp";
type PitcherHand = "righty" | "lefty" | "unknown";

export default function LineupOptimizer() {
  const [strategy, setStrategy] = React.useState<Strategy>("balanced");
  const [opponent, setOpponent] = React.useState<PitcherHand>("righty");

  return (
    <div className="flex flex-col items-center mt-10 space-y-6">
      <h2 className="text-2xl font-semibold">Lineup Optimizer</h2>

      {/* Optimization Strategy */}
      <div className="w-80 space-y-2">
        <Label htmlFor="strategy-select">Optimization Strategy</Label>
        <PrettySelect
          id="strategy-select"
          value={strategy}
          onValueChange={(v) => setStrategy(v as Strategy)}
          options={[
            { label: "Balanced Approach", value: "balanced" },
            { label: "Power Focused", value: "power" },
            { label: "Contact/Speed", value: "contact" },
            { label: "On-Base Priority", value: "obp" },
          ]}
        />
      </div>

      {/* Opposing Pitcher */}
      <div className="w-80 space-y-2">
        <Label htmlFor="opponent-select">Opposing Pitcher</Label>
        <PrettySelect
          id="opponent-select"
          value={opponent}
          onValueChange={(v) => setOpponent(v as PitcherHand)}
          options={[
            { label: "Right-handed", value: "righty" },
            { label: "Left-handed", value: "lefty" },
            { label: "Unknown", value: "unknown" },
          ]}
        />
      </div>
    </div>
  );
}
