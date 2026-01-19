# VALORANT Matchup Scouting Assistant

**Category 2 – Automated Scouting Report Generator**

An AI-powered scouting tool that generates coach-ready match preparation reports for VALORANT esports. This application fetches real match data from the **GRID Esports API**, performs statistical analysis and pattern detection, and uses **Google Gemini AI** to generate strategic insights.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![GRID](https://img.shields.io/badge/Data-GRID%20Esports%20API-orange)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Problem Statement

Coaches and analysts have access to rich GRID esports data, but converting that data into fast, match-ready decisions is slow, manual, and error-prone. Existing tools produce statistics and reports, but not **clear coaching actions**.

## 💡 Solution

This application is a **decision-support tool** that:
1. Uses **real GRID Esports API data** end-to-end
2. Generates a **structured, data-backed scouting report**
3. Uses **Google Gemini** to produce a **high-level strategic insight summary**
4. Outputs **coach-ready decisions** that explain *what to do* and *why it works*

### Guiding Principle
> **GRID provides facts. Gemini provides meaning. The coach gets decisions.**

## 🏗️ Architecture

### Two-Layer Report Design

**Layer 1 - Structured Scouting Report (GRID-Backed)**
- Match Overview
- Opponent Snapshot (best/worst maps, agents, star players)
- Key Strengths (with GRID metrics)
- Exploitable Weaknesses (with GRID metrics)
- Coach Recommendations (actionable, data-backed)

**Layer 2 - Strategic Insights (Gemini AI)**
- How does the opponent want to win?
- Where are they most vulnerable?
- What is the biggest risk in this matchup?
- Recommended high-level game plan

## 🔧 Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Backend | FastAPI |
| Data Source | GRID Esports API |
| AI Model | Google Gemini |
| Frontend | HTML5 + Bootstrap 5 + JavaScript |
| IDE | JetBrains PyCharm |
| AI Assistant | JetBrains Junie |

## 📁 Project Structure

```
app/
├── grid_client/           # GRID API integration
│   ├── __init__.py
│   ├── client.py          # API client with caching & logging
│   └── models.py          # Pydantic models for data validation
├── analysis/              # Statistics & pattern detection
│   ├── __init__.py
│   ├── stats.py           # Statistical calculations
│   ├── patterns.py        # Pattern detection algorithms
│   └── report_builder.py  # Structured report generation
├── ai/                    # Gemini AI integration
│   ├── __init__.py
│   ├── gemini_client.py   # Gemini API client
│   └── prompts.py         # Prompt templates
├── ui/                    # Web interface
│   ├── templates/
│   │   └── index.html     # Main UI template
│   └── static/
│       ├── app.js         # Frontend JavaScript
│       └── style.css      # Custom styles
├── main.py                # FastAPI application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
└── LICENSE                # MIT License
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11 or higher
- GRID Esports API key (get from [GRID](https://grid.gg))
- Google Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Jet Brains hack/app"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your API keys
   GRID_API_KEY=your_grid_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Open in browser**
   ```
   http://localhost:8000
   ```

## 📖 Usage Guide

### Basic Workflow

1. **Select Teams**
   - Choose "Our Team" (Team A) from the dropdown
   - Choose "Opponent" (Team B) from the dropdown
   - Select the analysis time window (30-180 days)

2. **Generate Report**
   - Click "Generate Report"
   - Wait for data fetching and analysis (10-30 seconds)

3. **Review Results**
   - **Layer 1**: Review factual GRID-backed data
   - **Layer 2**: Read Gemini's strategic interpretation
   - **Recommendations**: Check actionable coaching decisions

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/api/health` | GET | Health check |
| `/api/teams` | GET | List available teams |
| `/api/teams/{id}` | GET | Get team details |
| `/api/scout` | POST | Generate scouting report |

### Example API Call

```python
import requests

response = requests.post("http://localhost:8000/api/scout", json={
    "team_a_id": "team_sentinels",
    "team_b_id": "team_fnatic",
    "time_window_days": 90
})

report = response.json()
print(report["layer1_report"]["coach_recommendations"])
```

## 🔐 GRID API Usage

This application uses the GRID Esports API for:
- **Team metadata and rosters** - `/teams` endpoint
- **Recent matches/series** - `/matches` endpoint
- **Map-level results** - Match details
- **Agent pick frequency** - Player statistics
- **Player performance metrics** - ACS, K/D, ADR, etc.

All GRID data is:
- ✅ Logged with timestamps
- ✅ Cached (5-minute TTL)
- ✅ Transformed before AI use
- ✅ Traceable to report sections

## 🤖 Gemini AI Usage

Google Gemini is used to:
- Interpret pre-computed statistics (never raw data)
- Generate high-level strategic narratives
- Explain coaching implications
- Provide professional, coach-oriented summaries

**AI Safety Rules:**
- All numbers come from GRID
- AI receives pre-computed statistics only
- AI explains meaning, not calculations
- All AI outputs are logged

## 🛠️ Development

### JetBrains IDE Integration

This project was developed using:
- **JetBrains PyCharm** - Primary IDE
- **JetBrains Junie** - AI coding assistant for development

### Demo Mode

When API keys are not configured, the application runs in demo mode with:
- Sample VALORANT teams (Sentinels, Fnatic, LOUD, etc.)
- Realistic generated match data
- Template-based AI insights

## 📹 Demo Video Structure (3 Minutes)

1. **Problem Statement** (30s)
   - Show the challenge coaches face
   - Explain the gap between data and decisions

2. **Live Demo** (2m)
   - Select teams in the UI
   - Show GRID data fetching
   - Display Layer 1 structured report
   - Display Layer 2 Gemini insights
   - Highlight coach recommendations

3. **Technical Explanation** (30s)
   - GRID API integration
   - Gemini AI processing
   - JetBrains Junie assistance

## ✅ Success Criteria

- [x] Real GRID data visibly used
- [x] Clear separation of data vs insight
- [x] Coach can act immediately
- [x] Explainable, trustworthy AI output
- [x] Fully working end-to-end application

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **GRID Esports** - For the comprehensive esports data API
- **Google** - For the Gemini AI model
- **JetBrains** - For the excellent IDE and Junie AI assistant
- **VALORANT** - For the amazing esports ecosystem

---

**Built for the GRID Esports Data Challenge - Category 2: Automated Scouting Report Generator**
