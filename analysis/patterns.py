"""
Pattern detection for VALORANT scouting.

Identifies exploitable patterns and strategic tendencies from match data.
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
import logging

from grid_client.models import GridDataPackage, TeamMatchHistory

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Detects strategic patterns and tendencies from match data.

    Patterns include:
    - Map preferences and avoidances
    - Agent composition dependencies
    - Performance consistency
    - Situational strengths/weaknesses
    """

    def __init__(self, data: GridDataPackage):
        self.data = data
        self.team_a = data.team_a
        self.team_b = data.team_b
        logger.info("PatternDetector initialized")

    def detect_map_dependencies(self, team_history: TeamMatchHistory) -> List[Dict[str, Any]]:
        """
        Detect maps where team performance significantly differs from average.
        """
        dependencies = []
        overall_win_rate = team_history.win_rate

        for map_name, stats in team_history.map_stats.items():
            if stats.get("played", 0) < 2:
                continue

            map_win_rate = stats.get("win_rate", 0)
            diff = map_win_rate - overall_win_rate

            if abs(diff) > 15:  # Significant difference threshold
                dependencies.append({
                    "map": map_name,
                    "map_win_rate": round(map_win_rate, 1),
                    "overall_win_rate": round(overall_win_rate, 1),
                    "difference": round(diff, 1),
                    "type": "strength" if diff > 0 else "weakness",
                    "games_played": stats["played"],
                    "description": f"{'Strong' if diff > 0 else 'Weak'} on {map_name} ({round(map_win_rate, 1)}% vs {round(overall_win_rate, 1)}% overall)"
                })

        return sorted(dependencies, key=lambda x: abs(x["difference"]), reverse=True)

    def detect_agent_dependencies(self, team_history: TeamMatchHistory) -> List[Dict[str, Any]]:
        """
        Detect agent picks that correlate with win/loss patterns.
        """
        # Group matches by whether certain agents were picked
        agent_match_results = defaultdict(lambda: {"wins": 0, "losses": 0})
        team_player_ids = {p.id for p in team_history.team.roster}

        for match in team_history.matches:
            # Get agents picked by this team in this match
            agents_in_match = set()
            for pick in match.agent_picks:
                if pick.player_id in team_player_ids:
                    agents_in_match.add(pick.agent)

            won = match.winner_team_id == team_history.team.id

            for agent in agents_in_match:
                if won:
                    agent_match_results[agent]["wins"] += 1
                else:
                    agent_match_results[agent]["losses"] += 1

        # Analyze patterns
        dependencies = []
        overall_win_rate = team_history.win_rate

        for agent, results in agent_match_results.items():
            total = results["wins"] + results["losses"]
            if total < 3:  # Need minimum sample
                continue

            agent_win_rate = (results["wins"] / total) * 100
            diff = agent_win_rate - overall_win_rate

            if abs(diff) > 10:  # Significant threshold
                dependencies.append({
                    "agent": agent,
                    "with_agent_win_rate": round(agent_win_rate, 1),
                    "without_agent_win_rate": round(overall_win_rate, 1),
                    "difference": round(diff, 1),
                    "games_with_agent": total,
                    "type": "strength" if diff > 0 else "weakness",
                    "description": f"Win rate {'increases' if diff > 0 else 'decreases'} by {abs(round(diff, 1))}% with {agent}"
                })

        return sorted(dependencies, key=lambda x: abs(x["difference"]), reverse=True)

    def detect_form_patterns(self, team_history: TeamMatchHistory) -> Dict[str, Any]:
        """
        Analyze recent form and momentum patterns.
        """
        form = team_history.recent_form

        if len(form) < 3:
            return {
                "trend": "insufficient_data",
                "momentum": "neutral",
                "description": "Not enough recent matches to determine form"
            }

        recent_wins = form[:3].count("W")
        older_wins = form[3:].count("W") if len(form) > 3 else 0
        older_total = len(form) - 3 if len(form) > 3 else 1

        recent_rate = recent_wins / 3
        older_rate = older_wins / older_total if older_total > 0 else 0.5

        if recent_rate > older_rate + 0.2:
            trend = "improving"
            momentum = "positive"
        elif recent_rate < older_rate - 0.2:
            trend = "declining"
            momentum = "negative"
        else:
            trend = "stable"
            momentum = "neutral"

        # Detect streaks
        current_streak = 1
        streak_type = form[0] if form else "N/A"
        for i in range(1, len(form)):
            if form[i] == form[i-1]:
                current_streak += 1
            else:
                break

        return {
            "trend": trend,
            "momentum": momentum,
            "current_streak": current_streak,
            "streak_type": "winning" if streak_type == "W" else "losing",
            "recent_record": f"{recent_wins}-{3-recent_wins}",
            "description": f"Team is on a {current_streak}-{'win' if streak_type == 'W' else 'loss'} streak, form is {trend}"
        }

    def detect_opponent_strengths(self) -> List[Dict[str, Any]]:
        """
        Identify key strengths of the opponent team.
        """
        strengths = []
        opponent = self.team_b

        # Check win rate
        if opponent.win_rate >= 60:
            strengths.append({
                "category": "Overall Performance",
                "description": f"High overall win rate ({round(opponent.win_rate, 1)}%)",
                "metric": f"{opponent.win_rate:.1f}% win rate across {opponent.total_matches} matches",
                "severity": "high" if opponent.win_rate >= 70 else "medium"
            })

        # Check map dominance
        for map_name, stats in opponent.map_stats.items():
            if stats.get("played", 0) >= 3 and stats.get("win_rate", 0) >= 70:
                strengths.append({
                    "category": "Map Dominance",
                    "description": f"Dominant on {map_name}",
                    "metric": f"{stats['win_rate']:.1f}% win rate on {map_name} ({stats['wins']}-{stats['played']-stats['wins']})",
                    "severity": "high"
                })

        # Check form
        form_pattern = self.detect_form_patterns(opponent)
        if form_pattern["momentum"] == "positive":
            strengths.append({
                "category": "Momentum",
                "description": "Currently in strong form",
                "metric": form_pattern["description"],
                "severity": "medium"
            })

        # Check agent mastery
        agent_deps = self.detect_agent_dependencies(opponent)
        for dep in agent_deps[:2]:
            if dep["type"] == "strength" and dep["difference"] > 15:
                strengths.append({
                    "category": "Agent Mastery",
                    "description": f"Strong with {dep['agent']}",
                    "metric": f"{dep['with_agent_win_rate']}% win rate with {dep['agent']} ({dep['games_with_agent']} games)",
                    "severity": "medium"
                })

        return strengths[:5]  # Return top 5 strengths

    def detect_opponent_weaknesses(self) -> List[Dict[str, Any]]:
        """
        Identify exploitable weaknesses of the opponent team.
        """
        weaknesses = []
        opponent = self.team_b

        # Check poor maps
        for map_name, stats in opponent.map_stats.items():
            if stats.get("played", 0) >= 2 and stats.get("win_rate", 0) <= 40:
                weaknesses.append({
                    "category": "Map Weakness",
                    "description": f"Struggles on {map_name}",
                    "metric": f"{stats['win_rate']:.1f}% win rate on {map_name} ({stats['wins']}-{stats['played']-stats['wins']})",
                    "exploitability": "high",
                    "recommendation": f"Pick {map_name} in veto phase"
                })

        # Check form
        form_pattern = self.detect_form_patterns(opponent)
        if form_pattern["momentum"] == "negative":
            weaknesses.append({
                "category": "Poor Form",
                "description": "Currently in declining form",
                "metric": form_pattern["description"],
                "exploitability": "medium",
                "recommendation": "Apply early pressure to compound momentum issues"
            })

        # Check agent dependencies (negative)
        agent_deps = self.detect_agent_dependencies(opponent)
        for dep in agent_deps:
            if dep["type"] == "weakness" and dep["difference"] < -15:
                weaknesses.append({
                    "category": "Agent Dependency",
                    "description": f"Weaker with {dep['agent']}",
                    "metric": f"{dep['with_agent_win_rate']}% win rate with {dep['agent']}",
                    "exploitability": "medium",
                    "recommendation": f"Force uncomfortable agent compositions"
                })

        # Check if overly dependent on specific agents (remove them = problems)
        top_agents = sorted(opponent.agent_picks.items(), key=lambda x: x[1], reverse=True)
        if top_agents:
            top_agent, count = top_agents[0]
            total_picks = sum(opponent.agent_picks.values())
            if total_picks > 0:
                reliance = (count / total_picks) * 100
                if reliance > 30:
                    # Check win rate without this agent
                    for dep in agent_deps:
                        if dep["agent"] == top_agent and dep["type"] == "strength":
                            weaknesses.append({
                                "category": "Agent Dependency",
                                "description": f"Heavy reliance on {top_agent}",
                                "metric": f"{reliance:.1f}% of picks are {top_agent}, {dep['difference']:.1f}% higher win rate with {top_agent}",
                                "exploitability": "high",
                                "recommendation": f"Banning or countering {top_agent} could significantly impact performance"
                            })
                            break

        return weaknesses[:5]  # Return top 5 weaknesses

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate actionable coaching recommendations based on detected patterns.
        """
        recommendations = []

        opponent = self.team_b
        our_team = self.team_a

        # Map veto recommendations
        opponent_worst_maps = []
        for map_name, stats in opponent.map_stats.items():
            if stats.get("played", 0) >= 2:
                opponent_worst_maps.append((map_name, stats.get("win_rate", 50)))
        opponent_worst_maps.sort(key=lambda x: x[1])

        our_best_maps = []
        for map_name, stats in our_team.map_stats.items():
            if stats.get("played", 0) >= 2:
                our_best_maps.append((map_name, stats.get("win_rate", 50)))
        our_best_maps.sort(key=lambda x: x[1], reverse=True)

        # Find maps where we're strong AND they're weak
        for our_map, our_wr in our_best_maps[:3]:
            for opp_map, opp_wr in opponent_worst_maps[:3]:
                if our_map == opp_map and our_wr >= 55 and opp_wr <= 50:
                    advantage = our_wr - opp_wr
                    recommendations.append({
                        "action": f"Pick {our_map}",
                        "type": "map_pick",
                        "reasoning": f"Strong map advantage - Our {our_wr:.1f}% vs their {opp_wr:.1f}%",
                        "expected_impact": f"+{advantage:.1f}% expected win rate advantage",
                        "confidence": "high" if advantage > 20 else "medium",
                        "grid_data": f"Our record: {our_team.map_stats[our_map]['wins']}-{our_team.map_stats[our_map]['played']-our_team.map_stats[our_map]['wins']}, Their record: {opponent.map_stats[opp_map]['wins']}-{opponent.map_stats[opp_map]['played']-opponent.map_stats[opp_map]['wins']}"
                    })

        # Ban recommendations (opponent's best maps)
        opponent_best_maps = sorted(
            [(m, s.get("win_rate", 0)) for m, s in opponent.map_stats.items() if s.get("played", 0) >= 2],
            key=lambda x: x[1],
            reverse=True
        )

        for map_name, wr in opponent_best_maps[:2]:
            if wr >= 60:
                recommendations.append({
                    "action": f"Ban {map_name}",
                    "type": "map_ban",
                    "reasoning": f"Opponent's strong map - {wr:.1f}% win rate",
                    "expected_impact": f"Removes their best map option",
                    "confidence": "high",
                    "grid_data": f"Opponent's {map_name} record: {opponent.map_stats[map_name]['wins']}-{opponent.map_stats[map_name]['played']-opponent.map_stats[map_name]['wins']}"
                })

        # Agent-based recommendations
        agent_deps = self.detect_agent_dependencies(opponent)
        for dep in agent_deps[:2]:
            if dep["type"] == "strength" and dep["difference"] > 20:
                recommendations.append({
                    "action": f"Counter/Ban {dep['agent']}",
                    "type": "agent_strategy",
                    "reasoning": f"Opponent's win rate drops {abs(dep['difference']):.1f}% without {dep['agent']}",
                    "expected_impact": f"Forces suboptimal compositions",
                    "confidence": "medium",
                    "grid_data": f"Win rate with {dep['agent']}: {dep['with_agent_win_rate']}% ({dep['games_with_agent']} games)"
                })

        # Tactical recommendations based on star players
        from analysis.stats import StatsCalculator
        calc = StatsCalculator(self.data)
        opponent_stars = calc.get_star_players(opponent, top_n=1)

        if opponent_stars:
            star = opponent_stars[0]
            recommendations.append({
                "action": f"Focus {star['name']}",
                "type": "tactical",
                "reasoning": f"Star player averaging {star['avg_acs']} ACS, {star['kd_ratio']} K/D",
                "expected_impact": "Disrupting their star player reduces team effectiveness",
                "confidence": "high",
                "grid_data": f"{star['name']}: {star['avg_acs']} ACS, {star['kd_ratio']} K/D on {star['most_played_agent']}"
            })

        return recommendations[:6]  # Return top 6 recommendations
