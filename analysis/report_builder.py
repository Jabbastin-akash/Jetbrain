"""
Scouting Report Builder.

Constructs the structured scouting report (Layer 1) from analyzed GRID data.
This report serves as the factual foundation for AI insights.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging
import json

from grid_client.models import GridDataPackage
from analysis.stats import StatsCalculator
from analysis.patterns import PatternDetector

logger = logging.getLogger(__name__)


class MatchOverview(BaseModel):
    """Match overview section of the report."""
    team_a_name: str
    team_b_name: str
    team_a_region: Optional[str]
    team_b_region: Optional[str]
    matches_analyzed_team_a: int
    matches_analyzed_team_b: int
    analysis_time_window_days: int
    opponent_overall_win_rate: float
    opponent_recent_form: List[str]
    opponent_recent_form_summary: str
    head_to_head_record: Dict[str, Any]
    data_source: str = "GRID Esports API"


class OpponentSnapshot(BaseModel):
    """Opponent analysis snapshot."""
    best_maps: List[Dict[str, Any]]
    worst_maps: List[Dict[str, Any]]
    most_played_agents: List[Dict[str, Any]]
    star_players: List[Dict[str, Any]]


class StrengthWeakness(BaseModel):
    """Individual strength or weakness entry."""
    category: str
    description: str
    metric: str
    severity: Optional[str] = None
    exploitability: Optional[str] = None


class CoachRecommendation(BaseModel):
    """Coach-ready recommendation."""
    action: str
    type: str
    reasoning: str
    expected_impact: str
    confidence: str
    grid_data: str


class ScoutingReport(BaseModel):
    """
    Complete structured scouting report.

    This is Layer 1 - factual, GRID-backed data only.
    """
    # Metadata
    report_id: str
    generated_at: datetime
    data_source: str = "GRID Esports API"

    # Sections
    match_overview: MatchOverview
    opponent_snapshot: OpponentSnapshot
    key_strengths: List[StrengthWeakness]
    exploitable_weaknesses: List[StrengthWeakness]
    coach_recommendations: List[CoachRecommendation]

    # Raw stats for reference
    team_a_stats: Dict[str, Any] = Field(default_factory=dict)
    team_b_stats: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_json(self) -> str:
        """Convert report to JSON string."""
        return self.model_dump_json(indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return self.model_dump()


class ScoutingReportBuilder:
    """
    Builds comprehensive scouting reports from GRID data.

    The builder orchestrates:
    1. Statistical calculations
    2. Pattern detection
    3. Report assembly

    All data is traceable back to GRID.
    """

    def __init__(self, data: GridDataPackage):
        self.data = data
        self.stats = StatsCalculator(data)
        self.patterns = PatternDetector(data)
        logger.info("ScoutingReportBuilder initialized")

    def build_report(self) -> ScoutingReport:
        """
        Build the complete scouting report.

        Returns:
            ScoutingReport with all sections populated
        """
        logger.info("=== Building Scouting Report ===")

        # Generate unique report ID
        report_id = f"scout_{self.data.team_a.team.short_name}_{self.data.team_b.team.short_name}_{int(datetime.now().timestamp())}"

        # Build each section
        match_overview = self._build_match_overview()
        opponent_snapshot = self._build_opponent_snapshot()
        key_strengths = self._build_strengths()
        exploitable_weaknesses = self._build_weaknesses()
        coach_recommendations = self._build_recommendations()

        # Compile raw stats for reference
        team_a_stats = {
            "overall": self.stats.calculate_overall_stats(self.data.team_a),
            "maps": self.stats.calculate_map_stats(self.data.team_a),
            "agents": self.stats.calculate_agent_stats(self.data.team_a),
            "players": self.stats.calculate_player_stats(self.data.team_a)
        }

        team_b_stats = {
            "overall": self.stats.calculate_overall_stats(self.data.team_b),
            "maps": self.stats.calculate_map_stats(self.data.team_b),
            "agents": self.stats.calculate_agent_stats(self.data.team_b),
            "players": self.stats.calculate_player_stats(self.data.team_b)
        }

        report = ScoutingReport(
            report_id=report_id,
            generated_at=datetime.now(),
            data_source="GRID Esports API",
            match_overview=match_overview,
            opponent_snapshot=opponent_snapshot,
            key_strengths=key_strengths,
            exploitable_weaknesses=exploitable_weaknesses,
            coach_recommendations=coach_recommendations,
            team_a_stats=team_a_stats,
            team_b_stats=team_b_stats
        )

        logger.info(f"Report built: {report_id}")
        logger.info(f"  Strengths identified: {len(key_strengths)}")
        logger.info(f"  Weaknesses identified: {len(exploitable_weaknesses)}")
        logger.info(f"  Recommendations: {len(coach_recommendations)}")

        return report

    def _build_match_overview(self) -> MatchOverview:
        """Build the match overview section."""
        opponent_stats = self.stats.calculate_overall_stats(self.data.team_b)
        h2h_stats = self.stats.calculate_head_to_head_stats()

        return MatchOverview(
            team_a_name=self.data.team_a.team.name,
            team_b_name=self.data.team_b.team.name,
            team_a_region=self.data.team_a.team.region,
            team_b_region=self.data.team_b.team.region,
            matches_analyzed_team_a=self.data.team_a.total_matches,
            matches_analyzed_team_b=self.data.team_b.total_matches,
            analysis_time_window_days=self.data.time_window_days,
            opponent_overall_win_rate=opponent_stats["win_rate"],
            opponent_recent_form=opponent_stats["recent_form"],
            opponent_recent_form_summary=opponent_stats["recent_form_summary"],
            head_to_head_record=h2h_stats,
            data_source="GRID Esports API"
        )

    def _build_opponent_snapshot(self) -> OpponentSnapshot:
        """Build the opponent snapshot section."""
        return OpponentSnapshot(
            best_maps=self.stats.get_best_maps(self.data.team_b),
            worst_maps=self.stats.get_worst_maps(self.data.team_b),
            most_played_agents=self.stats.get_most_played_agents(self.data.team_b),
            star_players=self.stats.get_star_players(self.data.team_b)
        )

    def _build_strengths(self) -> List[StrengthWeakness]:
        """Build the key strengths section."""
        detected = self.patterns.detect_opponent_strengths()

        strengths = []
        for s in detected[:3]:  # Top 3
            strengths.append(StrengthWeakness(
                category=s["category"],
                description=s["description"],
                metric=s["metric"],
                severity=s.get("severity", "medium")
            ))

        return strengths

    def _build_weaknesses(self) -> List[StrengthWeakness]:
        """Build the exploitable weaknesses section."""
        detected = self.patterns.detect_opponent_weaknesses()

        weaknesses = []
        for w in detected[:3]:  # Top 3
            weaknesses.append(StrengthWeakness(
                category=w["category"],
                description=w["description"],
                metric=w["metric"],
                exploitability=w.get("exploitability", "medium")
            ))

        return weaknesses

    def _build_recommendations(self) -> List[CoachRecommendation]:
        """Build the coach recommendations section."""
        detected = self.patterns.generate_recommendations()

        recommendations = []
        for r in detected[:5]:  # Top 5
            recommendations.append(CoachRecommendation(
                action=r["action"],
                type=r["type"],
                reasoning=r["reasoning"],
                expected_impact=r["expected_impact"],
                confidence=r["confidence"],
                grid_data=r["grid_data"]
            ))

        return recommendations
