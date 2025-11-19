# Simulation API - Usage Guide

## Overview
The simulation endpoints take 9 already-sorted players and run Monte Carlo simulations to predict lineup performance using Bram's baseball simulator.

## Available Endpoints

### 1. Simulate by Player IDs (Recommended)
**Endpoint:** `POST /api/v1/simulator/simulate-by-ids/`

**Request Body:**
```json
{
  "player_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9],
  "num_games": 1000
}
```

**Parameters:**
- `player_ids` (required): Array of exactly 9 player IDs in batting order (1-9)
- `num_games` (optional): Number of games to simulate (default: 1000, min: 100, max: 100,000)

**Response:**
```json
{
  "lineup": ["Player 1", "Player 2", "Player 3", ...],
  "num_games": 1000,
  "avg_score": 5.234,
  "median_score": 5.0,
  "std_dev": 2.45,
  "min_score": 0,
  "max_score": 15,
  "score_distribution": {
    "0": 12,
    "1": 45,
    "2": 89,
    ...
  }
}
```

---

### 2. Simulate by Player Names
**Endpoint:** `POST /api/v1/simulator/simulate-by-names/`

**Request Body:**
```json
{
  "player_names": [
    "Guerrero Jr., Vladimir",
    "Bichette, Bo",
    "Springer, George",
    ...
  ],
  "num_games": 1000
}
```

**Parameters:**
- `player_names` (required): Array of exactly 9 player names in batting order
- `num_games` (optional): Number of games to simulate

---

### 3. Simulate by Team (Auto-lineup)
**Endpoint:** `POST /api/v1/simulator/simulate-by-team/`

**Request Body:**
```json
{
  "team_id": 1,
  "num_games": 1000
}
```

**Parameters:**
- `team_id` (required): Team ID
- `num_games` (optional): Number of games to simulate

**Note:** This automatically selects the top 9 players by plate appearances. Not sorted by algorithm.

---

## How It Works

### Flow:
```
9 Sorted Player IDs 
    ↓
[Fetch Player Stats from DB]
    ↓
[Convert to Batter Probabilities]
    ↓
[Run N Games with Monte Carlo Simulation]
    ↓
[Return Aggregate Statistics]
```

### Player Stats → Batter Probabilities:
The simulator converts each player's stats into outcome probabilities:
- Strikeout %
- In-play-out %
- Walk %
- Single %
- Double %
- Triple %
- Home run %

These must sum to 1.0 (100%).

### Simulation Process:
1. Create 9 Batter objects from player stats
2. Initialize Game with the lineup
3. Play each game play-by-play (at-bats, base running, scoring)
4. Repeat N times (default 1000)
5. Calculate aggregate stats (mean, median, std dev, distribution)

---

## Integration with Algorithm

### Workflow:
```python
# Step 1: Algorithm sorts players (future implementation)
sorted_player_ids = algorithm_create_lineup(unsorted_players)

# Step 2: Run simulation on sorted lineup
response = requests.post('/api/v1/simulator/simulate-by-ids/', {
    "player_ids": sorted_player_ids,
    "num_games": 5000
})

# Step 3: Get expected runs
expected_runs = response.json()['avg_score']
print(f"This lineup is expected to score {expected_runs:.2f} runs per game")
```

---

## Authentication
All endpoints require authentication. Include authorization header:
```
Authorization: Bearer <your_token>
```

---

## Error Handling

### Common Errors:

**400 Bad Request:**
- Not exactly 9 players
- Invalid num_games value
- Team doesn't have 9 players

**404 Not Found:**
- Player ID doesn't exist
- Player name not found
- Team ID doesn't exist

**500 Internal Server Error:**
- Simulation failed (check player stats)
- Missing required stats for probability calculation

---

## Example Usage (Python)

```python
import requests

# Assuming you have an auth token
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Simulate a lineup
data = {
    "player_ids": [45, 23, 89, 12, 67, 34, 78, 56, 90],
    "num_games": 5000
}

response = requests.post(
    "http://localhost:8000/api/v1/simulator/simulate-by-ids/",
    json=data,
    headers=headers
)

result = response.json()
print(f"Average score: {result['avg_score']:.2f} runs")
print(f"Standard deviation: {result['std_dev']:.2f}")
print(f"Range: {result['min_score']} to {result['max_score']} runs")
```

---

## Performance Notes

- **Simulation speed**: ~10,000 games/second
- **Recommended num_games**: 1000-5000 for balance of accuracy and speed
- **For testing**: Use 100 games (faster, less accurate)
- **For production**: Use 5000+ games (slower, more accurate)

---

## Next Steps

1. **Algorithm Integration**: Connect the lineup algorithm to automatically sort players
2. **Batch Simulations**: Compare multiple lineups simultaneously
3. **Optimization**: Run simulations on all possible permutations to find absolute best lineup
4. **Caching**: Cache simulation results for frequently tested lineups

---

## Files Involved

```
backend/
├── simulator/
│   ├── views.py                      # API endpoints
│   ├── serializers.py                # Request/response validation
│   ├── urls.py                       # URL routing
│   ├── application/
│   │   └── simulation_service.py     # Business logic
│   ├── infrastructure/
│   │   └── player_repository.py      # Data access
│   ├── domain/
│   │   └── entities.py               # Domain models
│   ├── batter.py                     # Batter class (from simulator lib)
│   ├── baseball.py                   # Game class (from simulator lib)
│   └── sim_engine.py                 # Core simulation logic
└── lib/
    └── baseball-simulator/           # Bram's simulator library
```

---

## Questions?

The simulation is fully functional and ready to use. Just call the endpoint with 9 player IDs in the order you want them to bat, and it will return expected performance metrics!
