"""
Pydantic models for GRID Esports API responses.
These models ensure data validation and type safety.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ValorantMap(str, Enum):
    """VALORANT competitive maps."""
    ASCENT = "Ascent"
    BIND = "Bind"
    HAVEN = "Haven"
    SPLIT = "Split"
    ICEBOX = "Icebox"
    BREEZE = "Breeze"
    FRACTURE = "Fracture"
    PEARL = "Pearl"
    LOTUS = "Lotus"
    SUNSET = "Sunset"
    ABYSS = "Abyss"


class ValorantAgent(str, Enum):
    """VALORANT agents."""
    # Duelists
    JETT = "Jett"
    PHOENIX = "Phoenix"
    REYNA = "Reyna"
    RAZE = "Raze"
    YORU = "Yoru"
    NEON = "Neon"
    ISO = "Iso"
    WAYLAY = "Waylay"
    # Initiators
    BREACH = "Breach"
    SOVA = "Sova"
    SKYE = "Skye"
    KAYO = "KAY/O"
    FADE = "Fade"
    GEKKO = "Gekko"
    # Controllers
    BRIMSTONE = "Brimstone"
    VIPER = "Viper"
    OMEN = "Omen"
    ASTRA = "Astra"
    HARBOR = "Harbor"
    CLOVE = "Clove"
    # Sentinels
    SAGE = "Sage"
    CYPHER = "Cypher"
    KILLJOY = "Killjoy"
    CHAMBER = "Chamber"
    DEADLOCK = "Deadlock"
    VYSE = "Vyse"


class Player(BaseModel):
    """Player information from GRID API."""
    id: str
    name: str
    nickname: str = ""
    team_id: Optional[str] = None
    role: Optional[str] = None
    country: Optional[str] = None


class Team(BaseModel):
    """Team information from GRID API."""
    id: str
    name: str
    short_name: str = ""
    logo_url: Optional[str] = None
    region: Optional[str] = None
    roster: List[Player] = Field(default_factory=list)


class MapResult(BaseModel):
    """Single map result within a match."""
    map_name: str
    team_a_score: int
    team_b_score: int
    team_a_side_first: str = "attack"  # attack or defense
    winner_team_id: str
    duration_seconds: Optional[int] = None


class AgentPick(BaseModel):
    """Agent pick information for a player in a match."""
    player_id: str
    player_name: str
    agent: str
    map_name: str
    match_id: str


class PlayerMatchStats(BaseModel):
    """Player statistics for a single match."""
    player_id: str
    player_name: str
    agent: str
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    acs: float = 0.0  # Average Combat Score
    adr: float = 0.0  # Average Damage per Round
    kast: float = 0.0  # Kill/Assist/Survive/Trade percentage
    first_kills: int = 0
    first_deaths: int = 0
    headshot_percentage: float = 0.0
    clutches_won: int = 0
    clutches_attempted: int = 0


class Match(BaseModel):
    """Match information from GRID API."""
    id: str
    team_a_id: str
    team_b_id: str
    team_a_name: str
    team_b_name: str
    winner_team_id: Optional[str] = None
    date: datetime
    tournament_name: Optional[str] = None
    best_of: int = 3
    maps_played: List[MapResult] = Field(default_factory=list)
    team_a_map_wins: int = 0
    team_b_map_wins: int = 0
    player_stats: List[PlayerMatchStats] = Field(default_factory=list)
    agent_picks: List[AgentPick] = Field(default_factory=list)


class PlayerStats(BaseModel):
    """Aggregated player statistics across multiple matches."""
    player_id: str
    player_name: str
    team_id: str
    matches_played: int = 0
    total_kills: int = 0
    total_deaths: int = 0
    total_assists: int = 0
    avg_acs: float = 0.0
    avg_adr: float = 0.0
    avg_kast: float = 0.0
    total_first_kills: int = 0
    total_first_deaths: int = 0
    avg_headshot_percentage: float = 0.0
    most_played_agents: List[Dict[str, Any]] = Field(default_factory=list)
    kd_ratio: float = 0.0


class TeamMatchHistory(BaseModel):
    """Team's match history with computed statistics."""
    team: Team
    matches: List[Match] = Field(default_factory=list)
    total_matches: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    map_stats: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    agent_picks: Dict[str, int] = Field(default_factory=dict)
    recent_form: List[str] = Field(default_factory=list)  # W/L sequence


class GridDataPackage(BaseModel):
    """Complete data package fetched from GRID for analysis."""
    team_a: TeamMatchHistory
    team_b: TeamMatchHistory
    head_to_head_matches: List[Match] = Field(default_factory=list)
    fetch_timestamp: datetime = Field(default_factory=datetime.now)
    time_window_days: int = 90
    data_source: str = "GRID Esports API"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
