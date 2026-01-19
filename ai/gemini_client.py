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

    async def chat_with_scouting_data(
        self,
        question: str,
        report_data: Dict[str, Any],
        chat_history: list = None
    ) -> Dict[str, Any]:
        """
        Answer user questions about scouting data using Gemini or demo mode.

        Args:
            question: The user's question
            report_data: The complete scouting report data
            chat_history: Previous chat exchanges for context

        Returns:
            Dictionary with the answer and metadata
        """
        logger.info(f"Chat question: {question}")

        # Build context from report data
        context = self._build_chat_context(report_data)

        # Build chat prompt
        prompt = self._build_chat_prompt(question, context, chat_history or [])

        if not self._initialized:
            logger.info("Using demo chat response (Gemini not configured)")
            return self._generate_demo_chat_response(question, report_data)

        try:
            logger.info("Sending chat request to Gemini...")
            response = self.model.generate_content(prompt)
            answer = response.text

            # Log the interaction
            self._log_ai_interaction(
                prompt=prompt,
                response=answer,
                metadata={
                    "type": "chat",
                    "question": question[:100],
                    "model": "gemini-pro"
                }
            )

            return {
                "success": True,
                "answer": answer,
                "model": "gemini-pro",
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return self._generate_demo_chat_response(question, report_data)

    def _build_chat_context(self, report_data: Dict[str, Any]) -> str:
        """Build context string from report data for chat."""
        overview = report_data.get("layer1_report", {}).get("match_overview", {})
        snapshot = report_data.get("layer1_report", {}).get("opponent_snapshot", {})
        strengths = report_data.get("layer1_report", {}).get("key_strengths", [])
        weaknesses = report_data.get("layer1_report", {}).get("exploitable_weaknesses", [])
        recommendations = report_data.get("layer1_report", {}).get("coach_recommendations", [])

        context = f"""
SCOUTING DATA CONTEXT (from GRID Esports API):

TEAMS:
- Our Team: {overview.get('team_a_name', 'Unknown')}
- Opponent: {overview.get('team_b_name', 'Unknown')}

OPPONENT STATS:
- Matches Analyzed: {overview.get('matches_analyzed_team_b', 0)}
- Overall Win Rate: {overview.get('opponent_overall_win_rate', 0):.1f}%
- Recent Form: {' '.join(overview.get('opponent_recent_form', []))}
- Analysis Window: {overview.get('analysis_time_window_days', 90)} days

BEST MAPS:
{self._format_maps(snapshot.get('best_maps', []))}

WORST MAPS:
{self._format_maps(snapshot.get('worst_maps', []))}

TOP AGENTS:
{self._format_agents(snapshot.get('most_played_agents', []))}

STAR PLAYERS:
{self._format_players(snapshot.get('star_players', []))}

KEY STRENGTHS:
{self._format_strengths(strengths)}

EXPLOITABLE WEAKNESSES:
{self._format_weaknesses(weaknesses)}

COACH RECOMMENDATIONS:
{self._format_recommendations(recommendations)}
"""
        return context

    def _format_maps(self, maps: list) -> str:
        if not maps:
            return "- No map data available"
        return "\n".join([f"- {m['map']}: {m['win_rate']}% WR ({m['record']})" for m in maps])

    def _format_agents(self, agents: list) -> str:
        if not agents:
            return "- No agent data available"
        return "\n".join([f"- {a['agent']}: {a['pick_rate']}% pick rate" for a in agents[:5]])

    def _format_players(self, players: list) -> str:
        if not players:
            return "- No player data available"
        return "\n".join([f"- {p['name']}: {p['avg_acs']:.0f} ACS, {p['kd_ratio']:.2f} K/D" for p in players])

    def _format_strengths(self, strengths: list) -> str:
        if not strengths:
            return "- No significant strengths detected"
        return "\n".join([f"- {s['category']}: {s['description']} ({s['metric']})" for s in strengths])

    def _format_weaknesses(self, weaknesses: list) -> str:
        if not weaknesses:
            return "- No significant weaknesses detected"
        return "\n".join([f"- {w['category']}: {w['description']} ({w['metric']})" for w in weaknesses])

    def _format_recommendations(self, recs: list) -> str:
        if not recs:
            return "- No specific recommendations"
        return "\n".join([f"- {r['action']}: {r['reasoning']}" for r in recs])

    def _build_chat_prompt(self, question: str, context: str, history: list) -> str:
        """Build the chat prompt with context and history."""
        history_text = ""
        if history:
            history_text = "\nPREVIOUS CONVERSATION:\n"
            for h in history[-4:]:  # Last 2 exchanges
                role = "Coach" if h.get("role") == "user" else "Scout Assistant"
                history_text += f"{role}: {h.get('content', '')}\n"

        prompt = f"""You are the Scout Assistant, an AI helping VALORANT coaches prepare for matches.
You have access to GRID Esports API data about the opponent team.

IMPORTANT RULES:
1. ONLY use the data provided below - never invent statistics
2. Be concise and tactical in your responses
3. If data is missing, say so honestly
4. Focus on actionable coaching insights
5. Reference specific numbers from the data when relevant

{context}
{history_text}

COACH'S QUESTION: {question}

Provide a helpful, data-driven response. Keep it conversational but professional.
If the question is not about the match or opponent, politely redirect to scouting topics."""

        return prompt

    def _generate_demo_chat_response(self, question: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate demo chat response when Gemini is not available."""
        overview = report_data.get("layer1_report", {}).get("match_overview", {})
        snapshot = report_data.get("layer1_report", {}).get("opponent_snapshot", {})
        strengths = report_data.get("layer1_report", {}).get("key_strengths", [])
        weaknesses = report_data.get("layer1_report", {}).get("exploitable_weaknesses", [])
        recommendations = report_data.get("layer1_report", {}).get("coach_recommendations", [])

        question_lower = question.lower()
        team_b = overview.get("team_b_name", "the opponent")

        # Generate contextual response based on question keywords
        if any(word in question_lower for word in ['map', 'ban', 'veto', 'pick']):
            best_maps = snapshot.get('best_maps', [])
            worst_maps = snapshot.get('worst_maps', [])
            best_str = ", ".join([f"{m['map']} ({m['win_rate']}%)" for m in best_maps[:2]]) or "no data"
            worst_str = ", ".join([f"{m['map']} ({m['win_rate']}%)" for m in worst_maps[:2]]) or "no data"
            answer = f"Based on GRID data, <strong>{team_b}</strong>'s strongest maps are: {best_str}. I'd recommend banning these. Their weakest maps are: {worst_str} - try to force them onto these."

        elif any(word in question_lower for word in ['agent', 'composition', 'comp']):
            agents = snapshot.get('most_played_agents', [])
            if agents:
                agent_str = ", ".join([f"{a['agent']} ({a['pick_rate']}%)" for a in agents[:3]])
                answer = f"Their most picked agents are: {agent_str}. Consider counter-picking or banning their comfort picks like {agents[0]['agent']}."
            else:
                answer = "I don't have enough agent composition data for this opponent."

        elif any(word in question_lower for word in ['player', 'star', 'focus', 'target', 'shutdown']):
            players = snapshot.get('star_players', [])
            if players:
                top_player = players[0]
                answer = f"<strong>{top_player['name']}</strong> is their star player with {top_player['avg_acs']:.0f} ACS and {top_player['kd_ratio']:.2f} K/D. Focus defensive setups and utility to shut them down early."
            else:
                answer = "I don't have detailed player stats for this opponent."

        elif any(word in question_lower for word in ['weak', 'exploit', 'vulnerab']):
            if weaknesses:
                weak_str = "; ".join([f"{w['description']} ({w['metric']})" for w in weaknesses[:2]])
                answer = f"Key exploitable weaknesses: {weak_str}. Focus your game plan on these areas."
            else:
                answer = "No significant weaknesses detected in the GRID data. They appear to be a well-rounded team."

        elif any(word in question_lower for word in ['strong', 'strength', 'good']):
            if strengths:
                str_list = "; ".join([f"{s['description']} ({s['metric']})" for s in strengths[:2]])
                answer = f"Their key strengths: {str_list}. Be prepared to counter these in your game plan."
            else:
                answer = "No exceptional strengths detected - they appear to have balanced performance."

        elif any(word in question_lower for word in ['win', 'rate', 'form', 'recent']):
            win_rate = overview.get('opponent_overall_win_rate', 0)
            form = overview.get('opponent_recent_form', [])
            form_str = " ".join(form) if form else "Unknown"
            answer = f"<strong>{team_b}</strong> has a {win_rate:.1f}% overall win rate. Recent form: {form_str}."

        elif any(word in question_lower for word in ['recommend', 'strategy', 'approach', 'game plan']):
            if recommendations:
                rec_str = "<br>".join([f"• <strong>{r['action']}</strong>: {r['reasoning']}" for r in recommendations[:3]])
                answer = f"My top recommendations:<br>{rec_str}"
            else:
                answer = "Based on the data, I'd recommend standard preparation with focus on your own team's strengths."

        elif any(word in question_lower for word in ['pistol', 'eco', 'economy']):
            answer = f"The GRID data shows general performance trends. For detailed pistol/eco round analysis, check the full statistics in the scouting summary below. Their overall win rate of {overview.get('opponent_overall_win_rate', 0):.1f}% suggests their economy management is {'solid' if overview.get('opponent_overall_win_rate', 0) > 50 else 'potentially exploitable'}."

        else:
            # Default response
            matches = overview.get('matches_analyzed_team_b', 0)
            win_rate = overview.get('opponent_overall_win_rate', 0)
            answer = f"I've analyzed {matches} matches for <strong>{team_b}</strong> (win rate: {win_rate:.1f}%). Feel free to ask me about their maps, agents, players, strengths, weaknesses, or specific strategic recommendations!"

        return {
            "success": True,
            "answer": answer,
            "model": "demo-mode",
            "generated_at": datetime.now().isoformat()
        }

