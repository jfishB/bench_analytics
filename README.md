# Bench Analytics

**Bench Analytics** is a web application that helps **baseball coaches** build the most effective **team lineup** against a chosen opponent.  
By analyzing player data and opponent characteristics, the app provides **data-driven lineup recommendations** that improve strategic decision-making.

---

## Overview

Coaches can:

- Maintain and manage a **player roster** (add, edit, and remove players).
- Select an **opponent team** to generate optimal matchups.
- Run **lineup optimization algorithms** based on player performance and opponent metrics.
- View results in an **intuitive and modern interface** built for ease of use during pre-game planning.

This project is designed for **sports analytics enthusiasts and coaching staff** who want to bring a quantitative edge to their baseball strategies.

---

## Features

- **Player Management:** Add, update, and remove players from your roster.
- **Opponent Selection:** Choose an opposing team for analysis.
- **Lineup Optimization:** Automatically compute the best batting order using performance data.
- **Interactive Frontend:** Clean, responsive UI built with React + Tailwind CSS.
- **Database Integration:** Persistent storage for rosters and matchups via PostgreSQL.
- **Containerized Setup:** Fully runnable using Docker and docker-compose.

---

## Tech Stack

**Frontend**

- React (TypeScript)
- Tailwind CSS

**Backend**

- Django 5 (Python)
- REST API architecture

**Database**

- PostgreSQL (via Docker Compose for local development)

**Dev Tools & Infrastructure**

- Docker
- Git & GitHub for version control
- ESLint + Prettier for clean and consistent code
- Django ORM for database management

---

## Getting Started

### 1. Clone the Repository

```
git clone https://github.com/<your-org-or-username>/bench_analytics.git
cd bench_analytics
```

### 2. Run with Docker

```
docker-compose up --build
```

This command will start the backend, frontend, and PostgreSQL services.

### 3. Access the App

Frontend: `http://localhost:3000`

Backend API: `http://localhost:8000`

## Contributors

Jeevesh Balendra,
Lea Palme,
Ilya Kononov,
Luke Pan,
Rashu Sharda

## License

This project is licensed under the MIT License.

## Future Improvements

Integration with live player statistics APIs.

Advanced matchup prediction models using ML.

Role-based authentication (Coach / Analyst).

Exportable reports for lineup results.
