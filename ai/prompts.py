"""
Prompt templates for Google Gemini AI.

These templates ensure consistent, coach-oriented AI outputs.
All prompts explicitly instruct Gemini to only interpret provided data.
"""


class PromptTemplates:
    """
    Collection of prompt templates for different scouting scenarios.

    Design principles:
    1. AI receives only pre-computed statistics
    2. AI explains meaning, not calculations
    3. AI must not invent statistics
    4. Output is professional and coach-oriented
    """

    STRATEGIC_INSIGHT_PROMPT = """You are an elite VALORANT esports analyst preparing a strategic briefing for a professional coaching staff. Your job is to interpret the scouting data provided and deliver actionable strategic insights.

## CRITICAL RULES:
1. ONLY use the statistics and data provided below - DO NOT invent any numbers
2. DO NOT make up player names, match results, or statistics
3. Focus on strategic implications and coaching decisions
4. Be concise and professional
5. Every insight must be traceable to the provided data

## SCOUTING DATA:

### Match Context
- Our Team: {team_a_name} ({team_a_region})
- Opponent: {team_b_name} ({team_b_region})
- Matches Analyzed: {matches_analyzed} (last {time_window} days)
- Data Source: GRID Esports API

### Opponent Overview
- Overall Win Rate: {opponent_win_rate}%
- Recent Form: {recent_form} ({recent_form_summary})
- Head-to-Head Record: {h2h_record}

### Opponent's Best Maps
{best_maps}

### Opponent's Worst Maps
{worst_maps}

### Opponent's Key Agents
{key_agents}

### Opponent's Star Players
{star_players}

### Identified Strengths (Data-Backed)
{strengths}

### Identified Weaknesses (Data-Backed)
{weaknesses}

### Preliminary Recommendations
{recommendations}

---

## YOUR TASK:

Provide a HIGH-LEVEL STRATEGIC INSIGHT SUMMARY that answers these questions:

1. **How does this opponent want to win?**
   - Based on their map preferences, agent compositions, and playstyle patterns

2. **Where are they most vulnerable?**
   - Specific exploitable weaknesses backed by the data

3. **What is the biggest risk in this matchup?**
   - What could go wrong for our team if we're not prepared

4. **Recommended Game Plan**
   - High-level strategic approach for this match
   - Map veto strategy summary
   - Key tactical focuses

## FORMAT REQUIREMENTS:
- Use clear section headers
- Be specific but concise
- Reference the provided statistics when making claims
- Write for a professional coaching audience
- No generic advice - everything must be specific to this matchup data

Begin your strategic insight summary:"""

    MAP_VETO_PROMPT = """Based on the following map statistics, provide map veto recommendations:

Our Team ({team_a_name}) Map Performance:
{team_a_maps}

Opponent ({team_b_name}) Map Performance:
{team_b_maps}

Provide:
1. Maps we should PICK (and why)
2. Maps we should BAN (and why)
3. Maps to let through (acceptable battlefield)

Be specific and reference the win rates provided."""

    PLAYER_FOCUS_PROMPT = """Analyze the opponent's player statistics and provide tactical recommendations:

Opponent Star Players:
{star_players}

Opponent Player Statistics:
{player_stats}

Provide:
1. Primary threat assessment - who is their carry
2. Suggested defensive focus
3. Trading opportunities

Reference the specific stats (ACS, K/D, FK/FD) in your analysis."""

    @classmethod
    def format_strategic_insight_prompt(cls, report_data: dict) -> str:
        """
        Format the strategic insight prompt with report data.

        Args:
            report_data: Dictionary containing scouting report data

        Returns:
            Formatted prompt string ready for Gemini
        """
        # Format best maps
        best_maps = "\n".join([
            f"- {m['map']}: {m['win_rate']}% win rate ({m['record']})"
            for m in report_data.get("opponent_snapshot", {}).get("best_maps", [])
        ]) or "No significant data available"

        # Format worst maps
        worst_maps = "\n".join([
            f"- {m['map']}: {m['win_rate']}% win rate ({m['record']})"
            for m in report_data.get("opponent_snapshot", {}).get("worst_maps", [])
        ]) or "No significant data available"

        # Format key agents
        key_agents = "\n".join([
            f"- {a['agent']}: picked {a['times_picked']} times ({a['pick_rate']}%)"
            for a in report_data.get("opponent_snapshot", {}).get("most_played_agents", [])
        ]) or "No significant data available"

        # Format star players
        star_players = "\n".join([
            f"- {p['name']}: {p['avg_acs']} ACS, {p['kd_ratio']} K/D on {p['most_played_agent']}"
            for p in report_data.get("opponent_snapshot", {}).get("star_players", [])
        ]) or "No significant data available"

        # Format strengths
        strengths = "\n".join([
            f"- [{s['category']}] {s['description']}: {s['metric']}"
            for s in report_data.get("key_strengths", [])
        ]) or "No major strengths identified"

        # Format weaknesses
        weaknesses = "\n".join([
            f"- [{w['category']}] {w['description']}: {w['metric']}"
            for w in report_data.get("exploitable_weaknesses", [])
        ]) or "No major weaknesses identified"

        # Format recommendations
        recommendations = "\n".join([
            f"- {r['action']}: {r['reasoning']} (Data: {r['grid_data']})"
            for r in report_data.get("coach_recommendations", [])
        ]) or "Pending strategic analysis"

        # Extract overview data
        overview = report_data.get("match_overview", {})
        h2h = overview.get("head_to_head_record", {})
        h2h_record = f"{h2h.get('team_a_wins', 0)}-{h2h.get('team_b_wins', 0)} ({h2h.get('matches_played', 0)} matches)" if h2h.get('matches_played', 0) > 0 else "No previous encounters"

        return cls.STRATEGIC_INSIGHT_PROMPT.format(
            team_a_name=overview.get("team_a_name", "Our Team"),
            team_a_region=overview.get("team_a_region", "Unknown"),
            team_b_name=overview.get("team_b_name", "Opponent"),
            team_b_region=overview.get("team_b_region", "Unknown"),
            matches_analyzed=overview.get("matches_analyzed_team_b", 0),
            time_window=overview.get("analysis_time_window_days", 90),
            opponent_win_rate=overview.get("opponent_overall_win_rate", 0),
            recent_form=" ".join(overview.get("opponent_recent_form", [])),
            recent_form_summary=overview.get("opponent_recent_form_summary", "Unknown"),
            h2h_record=h2h_record,
            best_maps=best_maps,
            worst_maps=worst_maps,
            key_agents=key_agents,
            star_players=star_players,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
