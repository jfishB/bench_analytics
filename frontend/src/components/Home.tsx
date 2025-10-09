import React, { useState, useEffect } from "react";

interface Player {
  id: number;
  name: string;
  team: string;
  created_at: string;
}

export function Home() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [players, setPlayers] = useState<Player[]>([]);
  const [newPlayer, setNewPlayer] = useState({
    name: "",
    team: "",
  });

  const fetchPlayers = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/players/");
      const data = await response.json();
      setPlayers(data);
      setMessage("");
    } catch (error) {
      console.error("Error fetching players:", error);
      setMessage("Error loading players from database");
    }
  };

  const addPlayer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8000/api/players/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newPlayer),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setNewPlayer({ name: "", team: "" });
        fetchPlayers();
        setMessage("Player added successfully!");
        setTimeout(() => setMessage(""), 3000);
      } else {
        setMessage(`Error: ${data.error || 'Failed to add player'}`);
      }
    } catch (error) {
      console.error("Error adding player:", error);
      setMessage("Error adding player");
    }
  };

  const deletePlayer = async (id: number, name: string) => {
    if (confirm(`Are you sure you want to delete ${name}?`)) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/players/${id}/`, {
          method: "DELETE",
        });
        if (response.ok) {
          fetchPlayers();
          setMessage("Player deleted successfully!");
          setTimeout(() => setMessage(""), 3000);
        }
      } catch (error) {
        console.error("Error deleting player:", error);
        setMessage("Error deleting player");
      }
    }
  };

  useEffect(() => {
    fetchPlayers();
  }, []);

  return (
    <div style={{ 
      maxWidth: '1000px', 
      margin: '0 auto', 
      padding: '3rem 2rem',
      backgroundColor: '#f7fafc',
      minHeight: '100vh'
    }}>
      {message && (
        <div style={{
          padding: '0.75rem 1rem',
          marginBottom: '2rem',
          color: '#2d3748',
          fontSize: '0.9rem'
        }}>
          {message}
        </div>
      )}

      {/* Add Player Form */}
      <div style={{ marginBottom: '3rem' }}>
        <h2 style={{
          fontSize: '1.1rem',
          fontWeight: '600',
          marginBottom: '1rem',
          color: '#1a202c'
        }}>
          Add New Player
        </h2>
        <form onSubmit={addPlayer}>
          <div style={{
            display: 'flex',
            gap: '1rem',
            marginBottom: '1rem',
            flexWrap: 'wrap'
          }}>
            <input
              type="text"
              placeholder="Player name"
              value={newPlayer.name}
              onChange={(e) => setNewPlayer({ ...newPlayer, name: e.target.value })}
              required
              style={{
                flex: '1',
                minWidth: '200px',
                padding: '0.625rem 0.75rem',
                border: '1px solid #cbd5e0',
                borderRadius: '4px',
                fontSize: '0.95rem',
                backgroundColor: 'white',
                boxSizing: 'border-box'
              }}
            />
            <input
              type="text"
              placeholder="Team"
              value={newPlayer.team}
              onChange={(e) => setNewPlayer({ ...newPlayer, team: e.target.value })}
              required
              style={{
                flex: '1',
                minWidth: '200px',
                padding: '0.625rem 0.75rem',
                border: '1px solid #cbd5e0',
                borderRadius: '4px',
                fontSize: '0.95rem',
                backgroundColor: 'white',
                boxSizing: 'border-box'
              }}
            />
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '0.625rem 1.5rem',
                backgroundColor: '#2b6cb0',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.95rem',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.6 : 1
              }}
            >
              {loading ? 'Adding...' : 'Add'}
            </button>
          </div>
        </form>
      </div>

      {/* Players List */}
      <div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem'
        }}>
          <h2 style={{
            fontSize: '1.1rem',
            fontWeight: '600',
            color: '#1a202c',
            margin: 0
          }}>
            Players
          </h2>
          <button
            onClick={fetchPlayers}
            disabled={loading}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'transparent',
              color: '#2b6cb0',
              border: '1px solid #2b6cb0',
              borderRadius: '4px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.5 : 1
            }}
          >
            Refresh
          </button>
        </div>
        
        {loading && players.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem',
            color: '#718096',
            fontSize: '0.95rem'
          }}>
            Loading...
          </div>
        ) : players.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem',
            color: '#718096',
            fontSize: '0.95rem'
          }}>
            No players yet
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse'
            }}>
              <thead>
                <tr style={{
                  borderBottom: '1px solid #cbd5e0'
                }}>
                  <th style={{
                    padding: '0.75rem 0.5rem',
                    textAlign: 'left',
                    fontWeight: '500',
                    color: '#718096',
                    fontSize: '0.875rem'
                  }}>Name</th>
                  <th style={{
                    padding: '0.75rem 0.5rem',
                    textAlign: 'left',
                    fontWeight: '500',
                    color: '#718096',
                    fontSize: '0.875rem'
                  }}>Team</th>
                  <th style={{
                    padding: '0.75rem 0.5rem',
                    textAlign: 'left',
                    fontWeight: '500',
                    color: '#718096',
                    fontSize: '0.875rem'
                  }}>Date</th>
                  <th style={{
                    padding: '0.75rem 0.5rem',
                    textAlign: 'right',
                    fontWeight: '500',
                    color: '#718096',
                    fontSize: '0.875rem'
                  }}></th>
                </tr>
              </thead>
              <tbody>
                {players.map((player) => (
                  <tr key={player.id} style={{
                    borderBottom: '1px solid #e2e8f0'
                  }}>
                    <td style={{
                      padding: '0.875rem 0.5rem',
                      color: '#2d3748',
                      fontSize: '0.95rem'
                    }}>{player.name}</td>
                    <td style={{
                      padding: '0.875rem 0.5rem',
                      color: '#2d3748',
                      fontSize: '0.95rem'
                    }}>{player.team}</td>
                    <td style={{
                      padding: '0.875rem 0.5rem',
                      color: '#718096',
                      fontSize: '0.875rem'
                    }}>{new Date(player.created_at).toLocaleDateString()}</td>
                    <td style={{
                      padding: '0.875rem 0.5rem',
                      textAlign: 'right'
                    }}>
                      <button
                        onClick={() => deletePlayer(player.id, player.name)}
                        disabled={loading}
                        style={{
                          padding: '0.375rem 0.75rem',
                          backgroundColor: 'transparent',
                          color: '#718096',
                          border: '1px solid #cbd5e0',
                          borderRadius: '4px',
                          fontSize: '0.875rem',
                          cursor: loading ? 'not-allowed' : 'pointer',
                          opacity: loading ? 0.5 : 1
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
