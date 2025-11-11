# roster app

## auto csv loading

the roster app can automatically load player data from csv files when django starts.

### how it works:
- when you run `python manage.py runserver`, django checks if you want to load a csv
- if the `LOAD_CSV` environment variable is set, it loads that file from the `data/` folder
- if not set, server starts normally without loading anything

### usage:

load a csv file:
```powershell
$env:LOAD_CSV='batter_stats_2025.csv'
python manage.py runserver
```

load with a specific year override:
```powershell
$env:LOAD_CSV='batter_stats_2025.csv'; $env:CSV_YEAR='2025'
python manage.py runserver
```

skip loading (default):
```powershell
python manage.py runserver
```

### what it does:
- checks if database tables exist
- reads the csv from `data/` folder
- imports new players and updates existing ones
- prints stats: how many imported, updated, skipped

thats p much it! ask me (luke) if you have any questions!
