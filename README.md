![Logo](assets/logo.png)

# BenchAnalytics

Bench Analytics is a web application designed to help baseball coaches build the most effective team lineup against a chosen opponent. By analyzing player data, it provides data-driven lineup recommendations to enhance strategic decision-making.

## Features

- Lineup Optimization – Automatically compute the most effective batting order based on player stats.

- Performance-Based Recommendations – Data-driven suggestions for batting order and strategic matchups.

- Detailed Player Stats – View individual player performance metrics, trends, and historical stats.

- Intuitive Frontend – Clean, responsive UI built with React + Tailwind CSS for easy pre-game planning.

- Algorithm Rationale – Explain the reasoning behind suggested lineups for transparency.

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
