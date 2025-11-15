# Simulator App

Django app for running Monte Carlo baseball game simulations.

## Architecture

This app follows **Clean Architecture** principles with clear separation of concerns:

```
simulator/
├── domain/                    # Pure business logic (no dependencies)
│   └── entities.py           # BatterStats, SimulationResult
├── application/              # Use cases / service layer
│   └── simulation_service.py # SimulationService
├── infrastructure/           # External dependencies (DB, etc.)
│   └── player_repository.py  # PlayerRepository
├── management/commands/      # CLI commands
│   └── simulate_lineup.py    # Command-line interface
├── serializers.py            # DRF request/response validation
├── views.py                  # REST API endpoints
├── urls.py                   # URL routing
├── batter.py                 # Core simulator: Batter class
├── baseball.py               # Core simulator: Game class
└── sim_engine.py             # Core simulator: orchestration
```

### Layer Responsibilities

- **Domain**: Pure Python entities with business logic, no external dependencies
- **Application**: Orchestrates use cases, converts domain entities to simulator objects
- **Infrastructure**: Handles database access, converts Django models to domain entities
- **API Layer**: REST endpoints using DRF serializers for validation

## Usage

### Command Line

Simulate by player IDs:
```bash
python manage.py simulate_lineup --player-ids "1,2,3,4,5,6,7,8,9" --games 1000
```

Simulate by player names:
```bash
python manage.py simulate_lineup --player-names "Player One,Player Two,..." --games 1000
```

Simulate by team (uses top 9 players by PA):
```bash
python manage.py simulate_lineup --team-id 1 --games 5000
```

### REST API

All endpoints require authentication.

#### Simulate by Player IDs
```
POST /api/v1/simulator/simulate-by-ids/
Content-Type: application/json

{
    "player_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "num_games": 1000
}
```

#### Simulate by Player Names
```
POST /api/v1/simulator/simulate-by-names/
Content-Type: application/json

{
    "player_names": ["Guerrero Jr., Vladimir", "Bichette, Bo", ...],
    "num_games": 1000
}
```

#### Simulate by Team
```
POST /api/v1/simulator/simulate-by-team/
Content-Type: application/json

{
    "team_id": 1,
    "num_games": 1000
}
```

### Response Format

All endpoints return:
```json
{
    "lineup": ["Player 1", "Player 2", ...],
    "num_games": 1000,
    "avg_score": 4.52,
    "median_score": 4.0,
    "std_dev": 2.34,
    "min_score": 0,
    "max_score": 15,
    "score_distribution": {
        "0": 45,
        "1": 82,
        "2": 134,
        ...
    }
}
```

## How It Works

### Monte Carlo Simulation

The simulator runs thousands of probabilistic baseball games to determine expected outcomes:

1. **Convert Stats to Probabilities**: Raw stats (H, 2B, 3B, HR, SO, BB, PA) → probabilities for each at-bat outcome
2. **Simulate At-Bats**: For each at-bat, randomly select outcome based on probabilities
3. **Game Mechanics**: Track bases, outs, innings with realistic baseball rules
4. **Aggregate Results**: Calculate average/median/std dev over thousands of games

### Probability Calculation

For a batter with these stats:
- PA: 680, H: 172, 2B: 34, 3B: 0, HR: 23, SO: 94, BB: 81

Probabilities:
- Strikeout: 94 / 680 = 13.8%
- Walk: 81 / 680 = 11.9%
- Single: (172 - 34 - 0 - 23) / 680 = 16.9%
- Double: 34 / 680 = 5.0%
- Triple: 0 / 680 = 0.0%
- Home Run: 23 / 680 = 3.4%
- Out: Remaining = 49.0%

### Game Simulation

Each game:
1. 9 innings with 3 outs per inning
2. Batters cycle through lineup
3. Advanced mechanics: stolen bases, sacrifice flies, double plays
4. Tracks runner advancement probabilistically
5. Returns final score

## Data Requirements

Players must have these fields populated:
- `pa` - Plate appearances
- `hit` - Total hits
- `double` - Doubles
- `triple` - Triples
- `home_run` - Home runs
- `strikeout` - Strikeouts
- `walk` - Walks

Import data using:
```bash
python manage.py import_test_data -f data/your_dataset.csv -t 1
```

CSV format:
```csv
"last_name, first_name",player_id,year,pa,hit,double,triple,home_run,strikeout,walk,team_id
"Guerrero Jr., Vladimir",665489,2025,680,172,34,0,23,94,81,1
...
```

## Testing

Run tests:
```bash
python manage.py test simulator
```

## Credits

Core simulation engine from: https://github.com/bramgrooten/baseball-simulator
