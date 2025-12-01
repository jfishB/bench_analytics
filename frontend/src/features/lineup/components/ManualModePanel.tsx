/**
 * ManualModePanel - Component for manual lineup creation with drag-and-drop
 */

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/ui/components/card";
import { Button } from "@/ui/components/button";
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
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Player } from "../../../shared/types";
import { Zap } from "lucide-react";

// Sortable player item component for drag and drop
interface SortablePlayerItemProps {
  player: Player;
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
      className="group relative overflow-hidden bg-white border rounded-xl p-3 shadow-sm cursor-move transition-all hover:shadow-md border-blue-100 hover:border-blue-300"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-blue-500/20 to-blue-500/0 opacity-0 group-hover:opacity-100 transition-opacity"></div>
      <div className="relative flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center text-white shadow-md bg-gradient-to-br from-[#1e3a8a] to-[#1e40af]">
            <span className="text-sm font-semibold">
              {player.batting_order || index + 1}
            </span>
          </div>
          <div>
            <div className="font-medium">{player.name}</div>
          </div>
        </div>
        <div>
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
    </div>
  );
}

interface ManualModePanelProps {
  lineupPlayers: Player[];
  battingOrderLineup: Player[];
  lineupName: string;
  saveStatus: "idle" | "saving" | "saved";
  onPlayerClick: (player: Player) => void;
  onLineupNameChange: (name: string) => void;
  onDragEnd: (event: DragEndEvent) => void;
  onSave: () => Promise<void>;
}

export function ManualModePanel({
  lineupPlayers,
  battingOrderLineup,
  lineupName,
  saveStatus,
  onPlayerClick,
  onLineupNameChange,
  onDragEnd,
  onSave,
}: ManualModePanelProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-900/10 rounded-lg">
              <Zap className="h-5 w-5 text-blue-900" />
            </div>
            <div>
              <CardTitle>Batting Order</CardTitle>
              <CardDescription>
                Drag players to rearrange the batting order
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={onDragEnd}
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
                onChange={(e) => onLineupNameChange(e.target.value)}
                placeholder="Enter lineup name..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <Button
              className={`w-full ${
                saveStatus === "saved" ? "bg-green-600 hover:bg-green-600" : ""
              } disabled:bg-gray-200 disabled:cursor-not-allowed`}
              disabled={!lineupName.trim() || saveStatus === "saving"}
              onClick={onSave}
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
  );
}

export default ManualModePanel;
