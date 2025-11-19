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
} from "../../../ui/components/card";
import { Button } from "../../../ui/components/button";
import PlayersOrderedList from "../../players/components/PlayersOrderedList";
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
      className="flex items-center bg-white border border-gray-200 rounded-lg p-3 shadow-sm cursor-move hover:bg-gray-50"
    >
      <div className="w-10 flex-shrink-0">
        <div className="h-8 w-8 rounded-full flex items-center justify-center font-semibold bg-primary text-white">
          {player.batting_order || index + 1}
        </div>
      </div>
      <div className="ml-3 flex-1">
        <div className="text-sm font-medium text-gray-900">{player.name}</div>
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
    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Selected Players</CardTitle>
          <CardDescription>
            Your 9 selected players - drag them to arrange batting order
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PlayersOrderedList
            players={lineupPlayers}
            onItemClick={onPlayerClick}
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
                saveStatus === "saved"
                  ? "bg-green-600 hover:bg-green-600"
                  : ""
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

