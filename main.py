"""
VALORANT Matchup Scouting Assistant - Main Application

FastAPI backend that orchestrates:
1. GRID Esports API data fetching
2. Statistical analysis and pattern detection
3. Google Gemini AI insights generation
4. Web UI for coaches and analysts

Category 2 - Automated Scouting Report Generator
Hackathon Entry for GRID Esports Data Challenge
"""

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging
import os

from grid_client import GridClient
from analysis import ScoutingReportBuilder
from ai import GeminiClient
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VALORANT Matchup Scouting Assistant",
    description="AI-powered scouting reports using GRID Esports data and Google Gemini",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "ui", "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "ui", "templates"))

# Initialize clients
grid_client: Optional[GridClient] = None
gemini_client: Optional[GeminiClient] = None


# ============================================================================
# Request/Response Models
# ============================================================================

class ScoutingRequest(BaseModel):
    """Request model for generating a scouting report."""
    team_a_id: str
    team_b_id: str
    time_window_days: int = 90


class TeamResponse(BaseModel):
    """Response model for team data."""
    id: str
    name: str
    short_name: str
    region: Optional[str] = None


# ============================================================================
# Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize clients on startup."""
    global grid_client, gemini_client

    logger.info("=== VALORANT Scouting Assistant Starting ===")
    logger.info("Initializing GRID client...")
    grid_client = GridClient()

    logger.info("Initializing Gemini client...")
    gemini_client = GeminiClient()

    settings = get_settings()
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("=== Startup Complete ===")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global grid_client
    if grid_client:
        await grid_client.close()
    logger.info("Application shutdown complete")


# ============================================================================
# Web UI Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main scouting interface."""
    return templates.TemplateResponse("index.html", {"request": request})


# ============================================================================
# API Routes
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "VALORANT Scouting Assistant"
    }


@app.get("/api/teams", response_model=List[TeamResponse])
async def get_teams(search: Optional[str] = Query(None, description="Search teams by name")):
    """
    Get available VALORANT teams.

    Fetches team data from GRID Esports API.
    """
    logger.info(f"API: Get teams (search={search})")

    try:
        teams = await grid_client.get_teams(search)
        return [
            TeamResponse(
                id=t.id,
                name=t.name,
                short_name=t.short_name,
                region=t.region
            )
            for t in teams
        ]
    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/teams/{team_id}")
async def get_team(team_id: str):
    """
    Get detailed information for a specific team.
    """
    logger.info(f"API: Get team {team_id}")

    try:
        team = await grid_client.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return {
            "id": team.id,
            "name": team.name,
            "short_name": team.short_name,
            "region": team.region,
            "roster": [
                {
                    "id": p.id,
                    "name": p.name,
                    "nickname": p.nickname,
                    "role": p.role
                }
                for p in team.roster
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scout")
async def generate_scouting_report(request: ScoutingRequest):
    """
    Generate a complete scouting report.

    This is the main endpoint that:
    1. Fetches GRID data for both teams
    2. Computes statistics and detects patterns
    3. Builds a structured scouting report
    4. Generates Gemini AI insights

    Returns both Layer 1 (factual) and Layer 2 (AI insights).
    """
    logger.info("=== Scouting Report Request ===")
    logger.info(f"Team A: {request.team_a_id}")
    logger.info(f"Team B: {request.team_b_id}")
    logger.info(f"Time window: {request.time_window_days} days")

    try:
        # Step 1: Fetch GRID data
        logger.info("Step 1: Fetching GRID data...")
        data_package = await grid_client.fetch_scouting_data(
            team_a_id=request.team_a_id,
            team_b_id=request.team_b_id,
            time_window_days=request.time_window_days
        )

        # Step 2: Build structured report
        logger.info("Step 2: Building structured report...")
        report_builder = ScoutingReportBuilder(data_package)
        report = report_builder.build_report()

        # Convert to dict for JSON response and AI processing
        report_dict = report.to_dict()

        # Step 3: Generate AI insights
        logger.info("Step 3: Generating Gemini AI insights...")
        ai_insights = await gemini_client.generate_strategic_insights(report_dict)

        logger.info("=== Scouting Report Complete ===")

        return {
            "success": True,
            "report_id": report.report_id,
            "generated_at": report.generated_at.isoformat(),
            "data_source": "GRID Esports API",

            # Layer 1: Structured factual report
            "layer1_report": {
                "match_overview": report_dict["match_overview"],
                "opponent_snapshot": report_dict["opponent_snapshot"],
                "key_strengths": report_dict["key_strengths"],
                "exploitable_weaknesses": report_dict["exploitable_weaknesses"],
                "coach_recommendations": report_dict["coach_recommendations"]
            },

            # Layer 2: AI-generated insights
            "layer2_insights": ai_insights,

            # Raw stats for advanced users
            "raw_stats": {
                "team_a": report_dict["team_a_stats"],
                "team_b": report_dict["team_b_stats"]
            }
        }

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/{report_id}")
async def get_report(report_id: str):
    """
    Retrieve a previously generated report.

    Note: In a production system, this would fetch from a database.
    Currently returns a placeholder for the demo.
    """
    # For demo purposes, return info about the report endpoint
    return {
        "message": "Report retrieval endpoint",
        "report_id": report_id,
        "note": "In production, this would retrieve cached reports from a database"
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if get_settings().debug else "An error occurred"
        }
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
