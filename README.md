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

## Lineup Optimizer Algorithm:

- Lineup optimizer algorithm utilizes modern sabermetric strategies to rate lineups
  
- Algorithm works cited and explaination: (https://docs.google.com/document/d/1Ueua5ibYRHZDD7kmZyFevb0vuWYnapy7pMlNSXTEjJo/edit?usp=sharing)

## Code Architecture

The project is split into two main services—frontend and backend—each organized according to the conventions of its respective framework.

**Backend (Django REST Framework)**:
- The backend follows a modular, app-based architecture, as this is the recommended Django practice to help maintain consistent naming conventions and independent testability.
- Each domain feature is encapsulated in its own Django app, functioning as a “mini-project” with its own models, serializers, views, and tests.
- Examples include:
  - `bash accounts/` — authentication, user management, JWT integration
  - `bash lineups/` — lineup creation, updating, and business logic
  - `bash simulation/` — sabermetrics engine, run-expectancy calculations, player projections

**Frontend (TypeScript + React/Next.js)**:
- The frontend uses a feature-based folder architecture, where related UI components, hooks, types, and services live together.
- Top-level structure:
  - `bash app/` — Next.js routing and server/client entry points
  - `bash core/` — global configuration (API client, auth helpers, global providers)
  - `bash features/` — every domain feature is isolated
    - `bash players/` — fetching, listing, player UI components
    - `bash lineup/` — lineup builder UI, forms, logic
  - `bash services/` — API service wrappers (players API, lineup API, auth API)
  - `bash shared/` — reusable UI components and utilities
  - `bash @types/` — shared TypeScript types and interfaces
- Naming conventions:

## SOLID Principles

**1. Single Responsibility Principle**
_"A class should have only one reason to change."_

Each hook or service handles one job:

- useRosterData → fetches and manages roster data
- usePlayerSelection → handles player selection rules
- useLineupCreation → manages the lineup-building workflow
- useSavedLineups → loads and caches saved lineups
- lineupService → API calls and data shaping
- AuthContext → authentication and tokens

Because each piece has a narrow focus, changes stay contained.

**2. Open/Closed Principle**
_"Software entities should be open for extension, closed for modification."_

The system without rewriting existing code:

- Design tokens give you a stable base for spacing, colors, and type.
- New components can build on those tokens or add their own.
- UI composition (like Radix primitives or adding new tabs) lets you add features without touching what’s already there.

**3. Liskov Substitution Principle**
_"Objects of a supertype should be replaceable with objects of a subtype."_

Anything built on the same interface can be swapped in:

- All data hooks return { loading, data, error }, so components can switch between them easily.
- Components follow standard prop patterns, making it simple to replace or enhance them.

**4. Interface Segregation Principle**
_"Clients should not be forced to depend on interfaces they don't use."_

Types and services stay focused:

- Player, SavedLineup, GeneratedLineup, etc., each serve specific purposes.
- Components only import what they need.
- Service functions are small and targeted—fetching players, saving lineups, running simulations.

No one is forced to pull in a giant “everything” interface.

**5. Dependency Inversion Principle**
_"High-level modules should not depend on low-level modules. Both should depend on abstractions."_

High-level components rely on abstractions, not on raw implementations:

- Pages use hooks like useRosterData() instead of calling APIs directly.
- Switching data sources (REST → GraphQL → local mocks) only touches the service layer.
- UI stays clean and unaffected by backend changes.

This architecture ensures that business logic is testable, UI components are reusable, and changes to external dependencies (like API endpoints) don't ripple through the entire codebase.

### Design Patterns

**1. Observer Pattern**

Components react automatically to shared state changes. Context, custom hooks, and event-driven auth updates all work as the “subject,” while subscribed components re-render as observers.

**2. Strategy Pattern**

Different behaviors are swapped in at runtime: lineup generation modes, authentication flows, and data-fetching approaches (API, cached, or mock data).

**3. Facade Pattern**

Service files and custom hooks hide complex logic—API calls, caching, validation—behind simple functions that the rest of the app can use without touching the underlying messiness.

**4. Builder Pattern**

More complex structures (like manual lineups or multi-step configuration objects) are assembled piece by piece, keeping the flow easy to follow and modify.

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
