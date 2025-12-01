<p align="center">
  <img src="assets/logo.png" alt="Project Logo" width="400"/>
</p>

Bench Analytics is a web application designed to help baseball coaches build the most effective team lineup. Py combining a lineup opitimizing algorithm and a run per game simulator Bench Analytics provides highlevel baseball analytics to enhance strategic decision-making.

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

## code architecture 
## System Architecutre 
## Hosted connected ...
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

## Hosting Instructions
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
# TODO: add command for filling the datavase 
python manage.py migrate   # apply database migrations
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
