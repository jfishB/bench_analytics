import { useState } from "react";
import { Button } from "../components/ui/button";

const API_BASE_URL = "http://localhost:8001/api";

interface Player {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export default function Lineup() {
  const [playerName, setPlayerName] = useState("");
  const [message, setMessage] = useState("");
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchPlayers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/players/`);
      const data = await response.json();
      setPlayers(data.players || []);
    } catch (error) {
      console.error("Error fetching players:", error);
      setMessage("Error fetching players");
    }
  };

  const handleAdd = async () => {
    if (playerName.trim() === "") {
      setMessage("Please enter a name first");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/players/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: playerName }),
      });

      if (response.ok) {
        const newPlayer = await response.json();
        setMessage(`Player "${newPlayer.name}" added successfully!`);
        setPlayerName(""); // clear input
        fetchPlayers(); // refresh the list
      } else {
        const error = await response.json();
        setMessage(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error("Error adding player:", error);
      setMessage("Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (playerId: number, playerName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${playerName}"?`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/players/${playerId}/`, {
        method: "DELETE",
      });

      if (response.ok) {
        const result = await response.json();
        setMessage(
          result.message || `Player "${playerName}" deleted successfully!`
        );
        fetchPlayers(); // refresh the list
      } else {
        const error = await response.json();
        setMessage(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error("Error deleting player:", error);
      setMessage("Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center mt-10 space-y-4">
      <h2 className="text-2xl">Lineup Optimizer Page</h2>

      {/* Fetch players button */}
      <Button onClick={fetchPlayers} variant="outline">
        Load Players
      </Button>

      {/* Input box */}
      <input
        type="text"
        value={playerName}
        onChange={(e) => setPlayerName(e.target.value)}
        placeholder="Enter player name"
        className="border rounded px-3 py-2 w-64"
      />

      {/* Add player button */}
      <Button onClick={handleAdd} disabled={loading}>
        {loading ? "Adding..." : "Add Player"}
      </Button>

      {/* Feedback message */}
      {message && <p className="mt-4 text-lg">{message}</p>}

      {/* Players list */}
      {players.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">Current Players:</h3>
          <ul className="space-y-2">
            {players.map((player) => (
              <li
                key={player.id}
                className="flex items-center justify-between bg-gray-50 p-3 rounded-lg"
              >
                <span className="text-sm">
                  {player.name} (ID: {player.id})
                </span>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDelete(player.id, player.name)}
                  disabled={loading}
                >
                  Delete
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
