# VALORANT Matchup Scouting Assistant

Category: Category 2 – Automated Scouting Report Generator

This app uses real GRID Esports API data to generate structured scouting reports, then uses Google Gemini to produce executive strategic insights. Coaches get clear, actionable decisions with traceable evidence.

## Tech Stack
- Python 3.11+
- FastAPI
- GRID Esports API
- Google Gemini
- UI: Bootstrap + vanilla JS
- License: MIT

## Setup
1. Create `.env.local` (not committed). Example:
```
GRID_API_KEY=YOUR_GRID_KEY
GEMINI_API_KEY=YOUR_GEMINI_KEY
GRID_API_BASE_URL=https://api.grid.gg
DEBUG=true
CACHE_TTL_SECONDS=300
```
2. Ensure `.gitignore` includes `.env.local`.
3. Install dependencies:
```
pip install -r app/requirements.txt
```

## Run
```
python app/run_server.py
```
Open http://localhost:8000.

## Demo Flow
- Select teams
- Choose time window
- Generate report
- Chat with the Match Assistant to ask tactical questions

## Security
- Secrets are loaded from `.env.local` and never committed.
- All AI inputs/outputs are logged.

## License
MIT
