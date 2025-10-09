import { useState } from "react";
import { Button } from "../components/ui/button";

export default function Lineup() {
  const [playerName, setPlayerName] = useState("");
  const [message, setMessage] = useState("");

  const handleAdd = () => {
    if (playerName.trim() === "") {
      setMessage("Please enter a name first");
      return;
    }
    setMessage(`${playerName} Added`);
    setPlayerName(""); // clear input
  };

  const handleDelete = () => {
    setMessage("Player deleted");
  };

  return (
    <div className="flex flex-col items-center mt-10 space-y-4">
      <h2 className="text-2xl">Lineup Optimizer Page</h2>

      {/* Input box */}
      <input
        type="text"
        value={playerName}
        onChange={(e) => setPlayerName(e.target.value)}
        placeholder="Enter player name"
        className="border rounded px-3 py-2 w-64"
      />

      {/* Add player button */}
      <Button onClick={handleAdd}>Add Player</Button>
\\\
      {/* Delete player button */}
      <Button variant="destructive" onClick={handleDelete}>
        Delete Player
      </Button>

      {/* Feedback message */}
      {message && <p className="mt-4 text-lg">{message}</p>}
    </div>
  );
}