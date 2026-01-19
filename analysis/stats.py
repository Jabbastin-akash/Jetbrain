"""
Statistical calculations for VALORANT match data.

All statistics are computed from GRID data with full traceability.
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
import logging

from grid_client.models import GridDataPackage, Match, TeamMatchHistory, PlayerMatchStats

logger = logging.getLogger(__name__)


class StatsCalculator:
    """
    Computes statistics from GRID match data.

    All calculations are transparent and traceable.
    """

    def __init__(self, data: GridDataPackage):
        self.data = data
        self.team_a = data.team_a
        self.team_b = data.team_b
        logger.info("StatsCalculator initialized")

    def calculate_overall_stats(self, team_history: TeamMatchHistory) -> Dict[str, Any]:
        """Calculate overall team statistics."""
        return {
            "total_matches": team_history.total_matches,
            "wins": team_history.wins,
            "losses": team_history.losses,
            "win_rate": round(team_history.win_rate, 1),
            "recent_form": team_history.recent_form,
            "recent_form_summary": self._summarize_form(team_history.recent_form)
        }

    def _summarize_form(self, form: List[str]) -> str:
        """Summarize recent form into text."""
        if not form:
            return "No recent matches"

        wins = form.count("W")
        total = len(form)

        if wins == total:
            return f"Perfect form ({wins}/{total} wins)"
        elif wins >= total * 0.8:
            return f"Excellent form ({wins}/{total} wins)"
        elif wins >= total * 0.6:
            return f"Good form ({wins}/{total} wins)"
        elif wins >= total * 0.4:
            return f"Mixed form ({wins}/{total} wins)"
        else:
            return f"Poor form ({wins}/{total} wins)"

    def calculate_map_stats(self, team_history: TeamMatchHistory) -> Dict[str, Dict[str, Any]]:
        """Calculate per-map statistics."""
        map_stats = {}

        for map_name, stats in team_history.map_stats.items():
            played = stats.get("played", 0)
            wins = stats.get("wins", 0)
            rounds_won = stats.get("rounds_won", 0)
            rounds_lost = stats.get("rounds_lost", 0)

            win_rate = (wins / played * 100) if played > 0 else 0
            round_diff = rounds_won - rounds_lost
            avg_round_diff = round_diff / played if played > 0 else 0

            map_stats[map_name] = {
                "played": played,
                "wins": wins,
                "losses": played - wins,
                "win_rate": round(win_rate, 1),
                "rounds_won": rounds_won,
                "rounds_lost": rounds_lost,
                "round_differential": round_diff,
                "avg_round_differential": round(avg_round_diff, 1)
            }

        return map_stats

    def get_best_maps(self, team_history: TeamMatchHistory, top_n: int = 3) -> List[Dict[str, Any]]:
        """Get team's best performing maps."""
        map_stats = self.calculate_map_stats(team_history)

        # Filter maps with at least 2 games played
        qualified_maps = {k: v for k, v in map_stats.items() if v["played"] >= 2}

        # Sort by win rate, then by round differential
        sorted_maps = sorted(
            qualified_maps.items(),
            key=lambda x: (x[1]["win_rate"], x[1]["avg_round_differential"]),
            reverse=True
        )

        return [
            {
                "map": name,
                "win_rate": stats["win_rate"],
                "record": f"{stats['wins']}-{stats['losses']}",
                "avg_round_diff": stats["avg_round_differential"]
            }
            for name, stats in sorted_maps[:top_n]
        ]

    def get_worst_maps(self, team_history: TeamMatchHistory, top_n: int = 3) -> List[Dict[str, Any]]:
        """Get team's worst performing maps."""
        map_stats = self.calculate_map_stats(team_history)

        # Filter maps with at least 2 games played
        qualified_maps = {k: v for k, v in map_stats.items() if v["played"] >= 2}

        # Sort by win rate ascending
        sorted_maps = sorted(
            qualified_maps.items(),
            key=lambda x: (x[1]["win_rate"], x[1]["avg_round_differential"])
        )

        return [
            {
                "map": name,
                "win_rate": stats["win_rate"],
                "record": f"{stats['wins']}-{stats['losses']}",
                "avg_round_diff": stats["avg_round_differential"]
            }
            for name, stats in sorted_maps[:top_n]
        ]

    def calculate_agent_stats(self, team_history: TeamMatchHistory) -> Dict[str, Dict[str, Any]]:
        """Calculate agent pick statistics."""
        agent_stats = {}
        total_picks = sum(team_history.agent_picks.values())

        for agent, count in team_history.agent_picks.items():
            pick_rate = (count / total_picks * 100) if total_picks > 0 else 0
            agent_stats[agent] = {
                "times_picked": count,
                "pick_rate": round(pick_rate, 1)
            }

        return agent_stats

    def get_most_played_agents(self, team_history: TeamMatchHistory, top_n: int = 5) -> List[Dict[str, Any]]:
        """Get most frequently picked agents."""
        agent_stats = self.calculate_agent_stats(team_history)

        sorted_agents = sorted(
            agent_stats.items(),
            key=lambda x: x[1]["times_picked"],
            reverse=True
        )

        return [
            {
                "agent": name,
                "times_picked": stats["times_picked"],
                "pick_rate": stats["pick_rate"]
            }
            for name, stats in sorted_agents[:top_n]
        ]

    def calculate_player_stats(self, team_history: TeamMatchHistory) -> Dict[str, Dict[str, Any]]:
        """Calculate aggregated player statistics."""
        player_stats = defaultdict(lambda: {
            "matches": 0,
            "total_kills": 0,
            "total_deaths": 0,
            "total_assists": 0,
            "total_acs": 0,
            "total_adr": 0,
            "total_first_kills": 0,
            "total_first_deaths": 0,
            "agents_played": defaultdict(int)
        })

        team_player_ids = {p.id for p in team_history.team.roster}

        for match in team_history.matches:
            for stat in match.player_stats:
                if stat.player_id in team_player_ids:
                    ps = player_stats[stat.player_name]
                    ps["matches"] += 1
                    ps["total_kills"] += stat.kills
                    ps["total_deaths"] += stat.deaths
                    ps["total_assists"] += stat.assists
                    ps["total_acs"] += stat.acs
                    ps["total_adr"] += stat.adr
                    ps["total_first_kills"] += stat.first_kills
                    ps["total_first_deaths"] += stat.first_deaths
                    ps["agents_played"][stat.agent] += 1

        # Calculate averages
        result = {}
        for player_name, stats in player_stats.items():
            matches = stats["matches"]
            if matches > 0:
                kd = stats["total_kills"] / max(stats["total_deaths"], 1)
                result[player_name] = {
                    "matches_played": matches,
                    "avg_kills": round(stats["total_kills"] / matches, 1),
                    "avg_deaths": round(stats["total_deaths"] / matches, 1),
                    "avg_assists": round(stats["total_assists"] / matches, 1),
                    "kd_ratio": round(kd, 2),
                    "avg_acs": round(stats["total_acs"] / matches, 1),
                    "avg_adr": round(stats["total_adr"] / matches, 1),
                    "total_first_kills": stats["total_first_kills"],
                    "total_first_deaths": stats["total_first_deaths"],
                    "fk_fd_diff": stats["total_first_kills"] - stats["total_first_deaths"],
                    "most_played_agent": max(stats["agents_played"].items(), key=lambda x: x[1])[0] if stats["agents_played"] else "Unknown"
                }

        return result

    def get_star_players(self, team_history: TeamMatchHistory, top_n: int = 2) -> List[Dict[str, Any]]:
        """Identify star players based on performance metrics."""
        player_stats = self.calculate_player_stats(team_history)

        # Score players based on multiple metrics
        scored_players = []
        for name, stats in player_stats.items():
            score = (
                stats["avg_acs"] * 0.4 +
                stats["kd_ratio"] * 100 * 0.3 +
                stats["avg_adr"] * 0.2 +
                stats["fk_fd_diff"] * 5 * 0.1
            )
            scored_players.append({
                "name": name,
                "score": score,
                "avg_acs": stats["avg_acs"],
                "kd_ratio": stats["kd_ratio"],
                "avg_adr": stats["avg_adr"],
                "most_played_agent": stats["most_played_agent"],
                "fk_fd_diff": stats["fk_fd_diff"]
            })

        sorted_players = sorted(scored_players, key=lambda x: x["score"], reverse=True)
        return sorted_players[:top_n]

    def calculate_head_to_head_stats(self) -> Dict[str, Any]:
        """Calculate head-to-head statistics between the two teams."""
        h2h = self.data.head_to_head_matches

        if not h2h:
            return {
                "matches_played": 0,
                "team_a_wins": 0,
                "team_b_wins": 0,
                "team_a_win_rate": 0,
                "map_records": {}
            }

        team_a_id = self.team_a.team.id
        team_a_wins = sum(1 for m in h2h if m.winner_team_id == team_a_id)
        team_b_wins = len(h2h) - team_a_wins

        # Map-level breakdown
        map_records = defaultdict(lambda: {"team_a_wins": 0, "team_b_wins": 0})
        for match in h2h:
            for map_result in match.maps_played:
                if map_result.winner_team_id == team_a_id:
                    map_records[map_result.map_name]["team_a_wins"] += 1
                else:
                    map_records[map_result.map_name]["team_b_wins"] += 1

        return {
            "matches_played": len(h2h),
            "team_a_wins": team_a_wins,
            "team_b_wins": team_b_wins,
            "team_a_win_rate": round(team_a_wins / len(h2h) * 100, 1) if h2h else 0,
            "map_records": dict(map_records)
        }
