<p align="center">
  <img src="assets/logo.png" alt="Project Logo" width="400"/>
</p>

Bench Analytics is a web platform built to give baseball coaches the kind of strategic insight usually reserved for pro teams. It combines a lineup-optimization algorithm with a run-per-game simulator, allowing coaches to test different batting orders and immediately see how those choices could impact performance. Instead of relying on intuition alone, coaches get a data-driven view of how their roster works together, which helps them make smarter decisions before every game.

Built with amateur and youth coaches in mind, the tool gives teams without dedicated analysts a practical way to explore matchups, understand how player strengths stack together, and prepare a lineup with confidence.

## Authors

- [@jfishB](https://github.com/rashusharda)
- [@leajosephine12 ](https://github.com/leajosephine12)
- [@IlyaK27](https://github.com/IlyaK27)
- [@Xera-phix](https://github.com/Xera-phix)
- [@rashusharda](https://github.com/rashusharda)
- [@qiuethan](https://github.com/qiuethan)

## Features

- Lineup Optimization – Automatically compute the most effective batting order based on player stats.

- Lineup Builder - Build and save your own lineups.

- Run Prediction - Simulates thousands of games to estimate the expected runs per game.

- Detailed Player Stats – View individual player performance metrics, trends, and historical stats.

- Intuitive Frontend – Clean, responsive UI built with React + Tailwind CSS for easy pre-game planning.

- Algorithm Rationale – Explain the reasoning behind suggested lineups for transparency.

## Code Architecture

### SOLID Principles

**1. Single Responsibility Principle**
_"A class should have only one reason to change."_

Each custom hook and service has exactly one responsibility:

- `useRosterData.ts` - Only handles fetching and managing roster data from the API.
- `usePlayerSelection.ts` - Only manages player selection logic and validation (max 9 players).
- `useLineupCreation.ts` - Only handles the overall lineup creation workflow and state.
- `useSavedLineups.ts` - Only manages saved lineups fetching and caching.
- `lineupService.ts` - Only contains API calls and data transformation, no UI logic.
- `AuthContext.tsx` - Only handles authentication state and token management.

This separation means changes to roster fetching don't affect player selection logic, and authentication changes don't impact lineup creation.

**2. Open/Closed Principle**
_"Software entities should be open for extension, closed for modification."_

Our design token system uses this principle:

- Base design tokens define core spacing, colors, and typography.
- Component-specific tokens extend the base system without modifying it.
- New UI components can be added using existing tokens or extend with new ones.

Component composition pattern allows extension:

- UI components built with Radix primitives can be extended with additional props.
- New tabs can be added to the lineup optimizer without modifying existing tab logic.

**3. Liskov Substitution Principle**
_"Objects of a supertype should be replaceable with objects of a subtype."_

All custom hooks follow consistent interfaces:

- Every data-fetching hook returns `{ loading, data, error }` pattern.
- Any hook can be swapped for another following the same pattern.
- Components expect standard React props and can be substituted with enhanced versions.

**4. Interface Segregation Principle**
_"Clients should not be forced to depend on interfaces they don't use."_

Instead of monolithic interfaces, we use focused, specific types:

- `Player` type contains only essential fields used across components.
- `SavedLineup`, `GeneratedLineup`, and `SimulationRequest` are separate interfaces for specific use cases.
- Components only import the hooks and services they actually need.

API service functions are granular:

- `fetchPlayers()` - Only fetches roster data.
- `saveLineup()` - Only handles lineup persistence.
- `runSimulation()` - Only handles Monte Carlo simulation.
- Components use only the functions they need, not a giant service object.

**5. Dependency Inversion Principle**
_"High-level modules should not depend on low-level modules. Both should depend on abstractions."_

High-level components depend on hook abstractions, not concrete implementations:

- `LineupOptimizerPage` uses `useRosterData()` hook, not direct API calls.
- If we switch from REST API to GraphQL, only the service layer changes.
- Components don't know whether data comes from API, localStorage, or mock data.

This architecture ensures that business logic is testable, UI components are reusable, and changes to external dependencies (like API endpoints) don't ripple through the entire codebase. Each layer has clear boundaries and responsibilities, making the codebase maintainable as it grows.

## System Architecture

Bench Analytics follows a decoupled **Client-Server architecture**, separating the user interface from the data processing logic. This ensures modularity, allowing the frontend and backend to be developed, tested, and deployed independently.

## Hosted connected ...

**Local Development**:

- The project utilizes Docker and Docker Compose to containerize the PostgreSQL database and pgAdmin interface, ensuring a consistent data environment across different developer machines.
- The application services currently run on local runtimes (Node.js and Python).

**Production (Hosting & Architecture)**:

- The production environment is deployed on Render, where the backend service is hosted as a separate web services and the frontend service is hosted as a static site.
- The backend (Django REST Framework) runs as a Render web service and connects to a managed PostgreSQL database provided by Render while both being hosted in the same region in oregon.
- The frontend (Next.js/React) is deployed as a static site or web service on Render, and communicates directly with the backend API over HTTPS.
- Environment variables (API URLs, database credentials, JWT secrets, etc.) are securely stored in Render’s environment settings.
- All services are connected using Render’s internal networking to ensure secure and efficient communication.

**CI Pipelines**: GitHub Actions workflows (`bash frontend-ci.yml`, `bash backend-ci.yml`) are configured to automatically run linting (ESLint, Flake8), type checking (TypeScript), and unit tests (Jest, Pytest) on every push to `bash main` or `bash develop`.

## Tech Stack

**Frontend**

- **Core**: React 18 with TypeScript for type-safe component logic.
- **Styling**: Tailwind CSS for utility-first styling, using `bash tailwind-merge` and `bash clsx` for dynamic class management
- **UI Components**: Built with **Radix UI** primitives (`bash @radix-ui`) for accessible, headless interactive components.
- **Visualization: Recharts**: For rendering responsive baseball analytics charts.
- **Interactions: dnd-kit**: (`bash @dnd-kit`) for complex drag-and-drop lineup management.
- **State & Networking**: React Context API for global auth state; standard `bash fetch` wrapper for API consumption.

**Backend (REST API)**

- **Framework**: Django 5 with **Django REST Framework (DRF)**.
- **Authentication: SimpleJWT**: Implementation for stateless JSON Web Token (JWT) authentication.
- **Configuration**: `bash django-environ` for 12-factor app configuration management.
- **Testing**: `bash pytest` with `bash pytest-django` and `bash coverage` for robust backend testing.

**System Design & Connectivity**

1. **Client-Side**: The React frontend acts as the consumer. It manages application state and communicates with the backend via a RESTful API.
2. **API Layer**: The Django backend exposes structured endpoints. It handles business logic (lineup optimization algorithms), data validation, and serialization.

- **Communication**: JSON over HTTP.
- **Security**: Routes are protected via JWT Access/Refresh tokens.
- **CORS**: Configured to allow cross-origin requests, facilitating the split-stack development workflow.

3. **Data Layer**: The backend communicates with the PostgreSQL database using Django's ORM, ensuring database-agnostic queries and secure transaction management.

**Database**

- **Primary DB: PostgreSQL 16**: Chosen for its robustness with relational data (players, teams, lineups).

**Dev Tools & Infrastructure**

- Docker for local development
- Git & GitHub for version control
- ESLint + Prettier for clean and consistent code
- TypeScript for type checking
- Jest + Pytest for unit tests

## Run Locally

**Install Prerequisites**

```bash
   docker
   node
```

**Clone the project**

```bash
  git clone https://github.com/jfishB/bench_analytics.git
```

**Go to the project directory**

```bash
  cd bench_analytics
```

**Install dependencies**
Project root

```bash
python -m venv venv         # create virtual environment

source venv/bin/activate    # Linux/macOS
# or
venv\Scripts\Activate.ps1   # Windows PowerShell

pip install -r requirements.txt

```

Frontend

```bash
cd frontend
npm install
```

**Start the servers**
Open docker desktop

Project root

```bash
docker-compose up -d db
docker-compose ps
```

Frontend

```bash
cd frontend
npm run start
```

Backend

```bash
cd backend
python backend/manage.py makemigrations  # make database migrations if needed
python manage.py migrate                 # apply database migrations
python manage.py runserver
```

## Quick Start for Coaches

### Create a Lineup in 3 Steps:

1. Upload team csv
2. Choose 9 players
3. Click "Generate Lineup" - Algorithm creates optimal batting order

### Customize Your Lineup:

- Drag and drop players to reorder
- Save for future use

### Compare Lineups:

- Simulate multiple lineups
- Choose the best option based on expected runs

## License

This project is licensed under the MIT License.

## Roadmap

- Exportable reports for lineup results.
- Consider opponent pitcher in recommendation
- Easily load data from public API

## Support

For support, reach out via email or check the authors’ GitHub profiles.
