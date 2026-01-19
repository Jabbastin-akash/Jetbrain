"""
Google Gemini AI Client.

Handles communication with Google Gemini for generating strategic insights.
All AI inputs and outputs are logged for traceability.
"""

import google.generativeai as genai
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from config import get_settings
from ai.prompts import PromptTemplates

logger = logging.getLogger(__name__)


class GeminiError(Exception):
    """Custom exception for Gemini API errors."""
    pass


class GeminiClient:
    """
    Client for Google Gemini AI integration.

    Responsibilities:
    - Generate strategic insights from scouting reports
    - Log all AI interactions
    - Ensure AI safety rules are followed
    """

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.gemini_api_key
        self.model = None
        self._initialized = False

        if self.api_key and self.api_key != "your_gemini_api_key_here":
            self._initialize_client()
        else:
            logger.warning("Gemini API key not configured - using demo mode")

    def _initialize_client(self):
        """Initialize the Gemini client."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self._initialized = True
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._initialized = False

    def _log_ai_interaction(
        self,
        prompt: str,
        response: str,
        metadata: Dict[str, Any]
    ):
        """Log AI interaction for traceability."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_length": len(prompt),
            "response_length": len(response),
            "metadata": metadata
        }
        logger.info(f"AI Interaction: {json.dumps(log_entry)}")

        # Log first 500 chars of prompt and response for debugging
        logger.debug(f"Prompt preview: {prompt[:500]}...")
        logger.debug(f"Response preview: {response[:500]}...")

    async def generate_executive_insight(
        self,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate executive insight - a 30-second strategic brief for coaches.

        Args:
            report_data: Dictionary containing the structured scouting report

        Returns:
            Dictionary with executive insight and metadata
        """
        logger.info("=== Generating Executive Insight ===")

        # Format the prompt
        prompt = PromptTemplates.format_executive_insight_prompt(report_data)

        # Check if we're in demo mode
        if not self._initialized:
            logger.info("Using demo executive insight (Gemini not configured)")
            return self._generate_demo_executive_insight(report_data)

        try:
            # Generate response from Gemini
            logger.info("Sending executive insight request to Gemini...")
            response = self.model.generate_content(prompt)

            insight_text = response.text

            # Log the interaction
            self._log_ai_interaction(
                prompt=prompt,
                response=insight_text,
                metadata={
                    "team_a": report_data.get("match_overview", {}).get("team_a_name"),
                    "team_b": report_data.get("match_overview", {}).get("team_b_name"),
                    "model": "gemini-pro",
                    "type": "executive_insight"
                }
            )

            return {
                "success": True,
                "insight": insight_text,
                "generated_at": datetime.now().isoformat(),
                "model": "gemini-pro",
                "data_source": "GRID Esports API (interpreted by Gemini)"
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fall back to demo insight
            return self._generate_demo_executive_insight(report_data)

    def _generate_demo_executive_insight(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate demo executive insight when Gemini is not available.
        """
        overview = report_data.get("match_overview", {})
        snapshot = report_data.get("opponent_snapshot", {})
        strengths = report_data.get("key_strengths", [])
        weaknesses = report_data.get("exploitable_weaknesses", [])

        team_b = overview.get("team_b_name", "the opponent")
        best_maps = [m["map"] for m in snapshot.get("best_maps", [])[:2]]
        worst_maps = [m["map"] for m in snapshot.get("worst_maps", [])[:2]]
        top_agent = snapshot.get("most_played_agents", [{}])[0].get("agent", "their key agents")

        # Generate a realistic executive insight
        insight_text = f"{team_b} operates with a structured, map-control focused approach that maximizes their effectiveness on {' and '.join(best_maps) if best_maps else 'their comfort maps'}. "

        if weaknesses:
            weakness_desc = weaknesses[0].get("description", "early-game pressure")
            insight_text += f"However, they show consistent vulnerability to {weakness_desc.lower()}, particularly on {' and '.join(worst_maps) if worst_maps else 'maps outside their comfort zone'}. "

        if strengths:
            strength_desc = strengths[0].get("description", "their strategic depth")
            insight_text += f"The primary risk is underestimating {strength_desc.lower()}, which has proven decisive in their recent victories. "
        else:
            insight_text += f"The primary risk is allowing them onto {best_maps[0] if best_maps else 'their strongest maps'} where their {overview.get('opponent_overall_win_rate', 60):.0f}% win rate reflects their dominance. "

        insight_text += f"Our recommended approach: aggressive map veto discipline to force {worst_maps[0] if worst_maps else 'uncomfortable territory'}, early-round aggression to disrupt their setup plays, and targeted pressure on {top_agent} compositions to deny their standard strategies."

        return {
            "success": True,
            "insight": insight_text,
            "generated_at": datetime.now().isoformat(),
            "model": "demo-mode",
            "data_source": "GRID Esports API (demo interpretation)",
            "note": "Configure GEMINI_API_KEY for production AI insights"
        }

    async def generate_strategic_insights(
        self,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate strategic insights from a scouting report.

        Args:
            report_data: Dictionary containing the structured scouting report

        Returns:
            Dictionary with AI-generated insights and metadata
        """
        logger.info("=== Generating Strategic Insights ===")

        # Format the prompt
        prompt = PromptTemplates.format_strategic_insight_prompt(report_data)

        # Check if we're in demo mode
        if not self._initialized:
            logger.info("Using demo insights (Gemini not configured)")
            return self._generate_demo_insights(report_data)

        try:
            # Generate response from Gemini
            logger.info("Sending request to Gemini...")
            response = self.model.generate_content(prompt)

            insight_text = response.text

            # Log the interaction
            self._log_ai_interaction(
                prompt=prompt,
                response=insight_text,
                metadata={
                    "team_a": report_data.get("match_overview", {}).get("team_a_name"),
                    "team_b": report_data.get("match_overview", {}).get("team_b_name"),
                    "model": "gemini-pro"
                }
            )

            return {
                "success": True,
                "insights": insight_text,
                "generated_at": datetime.now().isoformat(),
                "model": "gemini-pro",
                "data_source": "GRID Esports API (interpreted by Gemini)"
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fall back to demo insights
            return self._generate_demo_insights(report_data)

    def _generate_demo_insights(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate demo insights when Gemini is not available.

        This provides realistic-looking insights for development/demo purposes.
        """
        overview = report_data.get("match_overview", {})
        snapshot = report_data.get("opponent_snapshot", {})
        strengths = report_data.get("key_strengths", [])
        weaknesses = report_data.get("exploitable_weaknesses", [])
        recommendations = report_data.get("coach_recommendations", [])

        team_a = overview.get("team_a_name", "Our Team")
        team_b = overview.get("team_b_name", "Opponent")

        # Build best maps string
        best_maps = snapshot.get("best_maps", [])
        best_map_names = [m["map"] for m in best_maps[:2]] if best_maps else ["various maps"]

        # Build worst maps string
        worst_maps = snapshot.get("worst_maps", [])
        worst_map_names = [m["map"] for m in worst_maps[:2]] if worst_maps else ["certain maps"]

        # Get star player
        star_players = snapshot.get("star_players", [])
        star_name = star_players[0]["name"] if star_players else "their star player"

        # Get key agent
        top_agents = snapshot.get("most_played_agents", [])
        key_agent = top_agents[0]["agent"] if top_agents else "their key agents"

        # Build recommendation summary
        rec_summary = []
        for r in recommendations[:3]:
            rec_summary.append(f"- **{r['action']}**: {r['reasoning']}")
        rec_text = "\n".join(rec_summary) if rec_summary else "- Standard preparation recommended"

        # Build strength summary
        strength_summary = []
        for s in strengths[:2]:
            strength_summary.append(f"- {s['description']} ({s['metric']})")
        strength_text = "\n".join(strength_summary) if strength_summary else "- No exceptional strengths identified"

        # Build weakness summary
        weakness_summary = []
        for w in weaknesses[:2]:
            weakness_summary.append(f"- {w['description']} ({w['metric']})")
        weakness_text = "\n".join(weakness_summary) if weakness_summary else "- No major weaknesses identified"

        insight_text = f"""# Strategic Insight Summary: {team_a} vs {team_b}

## 1. How Does {team_b} Want to Win?

Based on the GRID data analysis, **{team_b}** approaches matches with a clear strategic identity:

- **Map Control**: They favor {', '.join(best_map_names)} where they've shown strong performance
- **Star-Driven Plays**: {star_name} serves as their primary playmaker, often creating space for the team
- **Agent Composition**: Heavy reliance on {key_agent}, which forms the core of their tactical approach
- **Win Condition**: They look to establish early map control and convert first bloods into round wins

## 2. Where Are They Most Vulnerable?

The data reveals several exploitable weaknesses:

{weakness_text}

**Key Vulnerability**: Their performance drops significantly on {', '.join(worst_map_names)}, presenting clear map veto opportunities.

## 3. Biggest Risk in This Matchup

**Primary Risk**: If {team_b} gets onto their comfort maps ({', '.join(best_map_names)}), they become significantly harder to defeat. Their {overview.get('opponent_overall_win_rate', 50):.1f}% win rate reflects solid fundamentals.

**Secondary Risk**: {star_name} having an explosive game can swing the entire series momentum.

**Mitigation**: Strict map veto discipline and early-round aggression to disrupt their rhythm.

## 4. Recommended Game Plan

### Map Veto Strategy
{rec_text}

### Tactical Priorities
1. **Deny Comfort**: Force {team_b} onto their weaker maps through strategic vetoes
2. **Target Star Player**: Apply pressure to {star_name} - disrupt their FK attempts
3. **Composition Advantage**: Consider agent picks that counter their standard compositions

### Key Takeaways
{strength_text}

---

*This strategic summary is based on {overview.get('matches_analyzed_team_b', 0)} matches analyzed from GRID Esports API data over the last {overview.get('analysis_time_window_days', 90)} days. All statistics referenced are derived from actual match data.*"""

        return {
            "success": True,
            "insights": insight_text,
            "generated_at": datetime.now().isoformat(),
            "model": "demo-mode",
            "data_source": "GRID Esports API (demo interpretation)",
            "note": "Configure GEMINI_API_KEY for production AI insights"
        }
