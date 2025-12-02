<p align="center">
  <img src="assets/logo.png" alt="Project Logo" width="400"/>
</p>

Bench Analytics is a web application designed to help baseball coaches build the most effective team lineup against a chosen opponent. By analyzing player data, it provides data-driven lineup recommendations to enhance strategic decision-making.

## Features

- Lineup Optimization – Automatically compute the most effective batting order based on player stats.

- Performance-Based Recommendations – Data-driven suggestions for batting order and strategic matchups.

- Detailed Player Stats – View individual player performance metrics, trends, and historical stats.

- Intuitive Frontend – Clean, responsive UI built with React + Tailwind CSS for easy pre-game planning.

- Algorithm Rationale – Explain the reasoning behind suggested lineups for transparency.

## Technical Architecture

Bench Analytics follows a decoupled **Client-Server architecture**, separating the user interface from the data processing logic. This ensures modularity, allowing the frontend and backend to be developed, tested, and deployed independently.

## Tech Stack

**Frontend**

- **Core**: React 18 with TypeScript for type-safe component logic.
- **Styling**: Tailwind CSS for utility-first styling, using ```bash tailwind-merge``` and ```bash clsx``` for dynamic class management
- **UI Components**: Built with **Radix UI** primitives (```bash @radix-ui```) for accessible, headless interactive components.
- **Visualization: Recharts**: For rendering responsive baseball analytics charts.
- **Interactions: dnd-kit**: (```bash @dnd-kit```) for complex drag-and-drop lineup management.
- **State & Networking**: React Context API for global auth state; standard ```bash fetch``` wrapper for API consumption.

**Backend (REST API)**

- **Framework**: Django 5 with **Django REST Framework (DRF)**.
- **Authentication: SimpleJWT**: Implementation for stateless JSON Web Token (JWT) authentication.
- **Configuration**: ```bash django-environ``` for 12-factor app configuration management.
- **Testing**: ```bash pytest``` with ```bash pytest-django``` and ```bash coverage``` for robust backend testing.

**System Design & Connectivity**

1. **Client-Side**: The React frontend acts as the consumer. It manages application state and communicates with the backend via a RESTful API.
2. **API Layer**: The Django backend exposes structured endpoints. It handles business logic (lineup optimization algorithms), data validation, and serialization.
- **Communication**: JSON over HTTP.
- **Security**: Routes are protected via JWT Access/Refresh tokens.
- **CORS**: Configured to allow cross-origin requests, facilitating the split-stack development workflow.
3. **Data Layer**: The backend communicates with the PostgreSQL database using Django's ORM, ensuring database-agnostic queries and secure transaction management.

**Database**

- **Primary DB: PostgreSQL 16**: Chosen for its robustness with relational data (players, teams, lineups).

**Infrastructure & Hosting**

- **Local Development**: The project utilizes Docker and Docker Compose to containerize the PostgreSQL database and pgAdmin interface, ensuring a consistent data environment across different developer machines. The application services currently run on local runtimes (Node.js and Python).
- **CI Pipelines**: GitHub Actions workflows (```bash frontend-ci.yml```, ```bash backend-ci.yml```) are configured to automatically run linting (ESLint, Flake8), type checking (TypeScript), and unit tests (Jest, Pytest) on every push to ```bash main``` or ```bash develop```.

## Run Locally

**Clone the project**

```bash
  git clone https://github.com/jfishB/bench_analytics.git
```

**Go to the project directory**

```bash
  cd bench_analytics
```

**Install dependencies**

Frontend

```bash
  cd frontend
  npm install

```

Backend

```bash
cd backend
python -m venv venv         # create virtual environment
source venv/bin/activate    # Linux/macOS
# or
venv\Scripts\Activate.ps1   # Windows PowerShell

pip install -r requirements.txt
```

**Start the servers**

Frontend

```bash
cd frontend
npm run start
```

Backend

```bash
cd backend
python manage.py migrate   # apply database migrations
python manage.py runserver
```

## License

This project is licensed under the MIT License.

## Authors

- [@jfishB](https://github.com/rashusharda)
- [@leajosephine12 ](https://github.com/leajosephine12)
- [@IlyaK27](https://github.com/IlyaK27)
- [@Xera-phix](https://github.com/Xera-phix)
- [@rashusharda](https://github.com/rashusharda)
- [@qiuethan](https://github.com/qiuethan)

## Roadmap

- Generate multiple lineups to compare and contrast.

- Role-based authentication (Each coach see their respective lineup).
- Exportable reports for lineup results.

## Support

For support, reach out via email or check the authors’ GitHub profiles.
