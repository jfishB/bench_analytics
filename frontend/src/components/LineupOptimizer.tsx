import * as React from "react";
import { Label } from "./ui/label";
import PrettySelect from "./ui/pretty-select";

type Strategy = "balanced" | "power" | "contact" | "obp";
type PitcherHand = "righty" | "lefty" | "unknown";

export default function LineupOptimizer() {
  const [strategy, setStrategy] = React.useState<Strategy>("balanced");
  const [opponent, setOpponent] = React.useState<PitcherHand>("righty");

  return (
    <div className="flex flex-col items-center mt-10 space-y-6">
      <h2 className="text-2xl">Lineup Optimizer</h2>

      {/* Optimization Strategy */}
      <div className="w-80 space-y-2">
        <Label id="strategy-label">Optimization Strategy</Label>
        <PrettySelect
          labelId="strategy-label"
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
        <Label id="opp-label">Opposing Pitcher</Label>
        <PrettySelect
          labelId="opp-label"
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
