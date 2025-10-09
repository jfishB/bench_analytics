# 🎓 PostgreSQL Database Demo Guide

## How to Prove Data is in PostgreSQL (For Class Presentation)

### Method 1: Use the Web Interface (EASIEST) ⭐

1. **Go to** http://localhost:5173/
2. **Add a player** using the form:
   - Name: "LeBron James"
   - Team: "Lakers"
   - Points: 28
   - Click "💾 Save to PostgreSQL"
3. **Watch the data appear** in the table below
4. **Click "🔄 Refresh from Database"** to show it's pulling from PostgreSQL

### Method 2: Use Docker Desktop GUI

1. **Open Docker Desktop**
2. **Click on "Containers"** in the left sidebar
3. **Find** `bench_analytics_db` (should be running/green)
4. **Click the container** → Click "Exec" tab
5. **Type this command:**
   ```bash
   psql -U appuser -d appdb -c "SELECT * FROM api_player;"
   ```
6. **You'll see** all the players you added in a table format!

### Method 3: Use PowerShell/Terminal (MOST TECHNICAL) 🖥️

Open PowerShell and run:

```powershell
docker exec -it bench_analytics_db psql -U appuser -d appdb -c "SELECT * FROM api_player;"
```

**Output will look like:**
```
 id |     name      |   team   | points |         created_at
----+---------------+----------+--------+----------------------------
  1 | LeBron James  | Lakers   |     28 | 2025-10-08 23:50:12.345678
  2 | Stephen Curry | Warriors |     30 | 2025-10-08 23:51:45.678901
```

### Method 4: Show the Database Tables

```powershell
# List all tables
docker exec -it bench_analytics_db psql -U appuser -d appdb -c "\dt"

# Show table structure
docker exec -it bench_analytics_db psql -U appuser -d appdb -c "\d api_player"
```

---

## 🎯 Presentation Flow (Recommended)

1. **Start with the web interface** (http://localhost:5173/)
   - Show the empty table
   - Add 2-3 players live
   - Show data appearing in real-time

2. **Open Docker Desktop**
   - Show the running `bench_analytics_db` container
   - Click "Exec" tab and run: `psql -U appuser -d appdb -c "SELECT * FROM api_player;"`
   - Show the same data that's on the website

3. **Explain the flow:**
   ```
   Frontend (React) → Backend (Django) → PostgreSQL (Docker)
   ```

4. **Bonus: Show it persists**
   - Stop the servers
   - Restart them
   - Data is still there! (Stored in `pgdata/` folder)

---

## 🔧 Quick Commands Reference

### Start Everything:
```powershell
# Start database
docker compose up -d db

# Start backend (in one terminal)
cd backend
$env:POSTGRES_USER='appuser'; $env:POSTGRES_PASSWORD='secret'; $env:POSTGRES_DB='appdb'; $env:DB_PORT='5432'
python manage.py runserver

# Start frontend (in another terminal)
cd frontend
npm run dev
```

### Check Database Connection:
```powershell
docker exec -it bench_analytics_db psql -U appuser -d appdb -c "\conninfo"
```

### Count Records:
```powershell
docker exec -it bench_analytics_db psql -U appuser -d appdb -c "SELECT COUNT(*) FROM api_player;"
```

---

## 📸 Screenshot Checklist

For your presentation slides, capture:
- ✅ The web form with data entered
- ✅ The data table showing multiple players
- ✅ Docker Desktop showing the running container
- ✅ Terminal output from `SELECT * FROM api_player;`
- ✅ (Optional) pgdata/ folder showing actual database files

---

## ❓ Q&A Prep

**Q: How do we know it's using Postgres and not SQLite?**  
A: Show `backend/config/settings.py` - line ~78 shows `ENGINE: "django.db.backends.postgresql"`

**Q: Where is the data stored?**  
A: In Docker container + persisted in `pgdata/` folder (show folder in Explorer)

**Q: What happens if we delete a player from the database?**  
A: Run this to delete player with ID 1:
```powershell
docker exec -it bench_analytics_db psql -U appuser -d appdb -c "DELETE FROM api_player WHERE id=1;"
```
Then refresh the webpage - player is gone!

