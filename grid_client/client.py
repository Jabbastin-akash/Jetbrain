"""
GRID Esports API Client.

This module handles all communication with the GRID Esports API,
including authentication, data fetching, caching, and logging.

Note: GRID API structure is based on their GraphQL/REST endpoints.
This implementation includes both real API integration and demo data
for development/testing purposes.
"""

import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from cachetools import TTLCache
import json

from grid_client.models import (
    Team, Player, Match, MapResult, AgentPick,
    PlayerMatchStats, PlayerStats, TeamMatchHistory, GridDataPackage
)
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GridApiError(Exception):
    """Custom exception for GRID API errors."""
    pass


class GridClient:
    """
    Client for interacting with GRID Esports API.

    Handles:
    - API authentication
    - Data fetching with retry logic
    - Response caching
    - Comprehensive logging
    """

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.grid_api_base_url
        self.api_key = self.settings.grid_api_key
        self.cache = TTLCache(maxsize=100, ttl=self.settings.cache_ttl_seconds)

        # HTTP client configuration
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30.0
        )

        logger.info(f"GridClient initialized with base URL: {self.base_url}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _log_api_call(self, endpoint: str, params: dict, response_status: int):
        """Log API call details for traceability."""
        logger.info(f"GRID API Call: {endpoint}")
        logger.info(f"  Parameters: {json.dumps(params, default=str)}")
        logger.info(f"  Response Status: {response_status}")

    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        return ":".join(str(arg) for arg in args)

    async def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """
        Make an authenticated request to GRID API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            GridApiError: If API request fails
        """
        cache_key = self._get_cache_key(endpoint, json.dumps(params or {}, sort_keys=True))

        # Check cache first
        if cache_key in self.cache:
            logger.info(f"Cache hit for: {endpoint}")
            return self.cache[cache_key]

        try:
            response = await self.client.get(endpoint, params=params)
            self._log_api_call(endpoint, params or {}, response.status_code)

            if response.status_code == 200:
                data = response.json()
                self.cache[cache_key] = data
                return data
            elif response.status_code == 401:
                raise GridApiError("Authentication failed. Check GRID API key.")
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                return {}
            else:
                raise GridApiError(f"API error: {response.status_code} - {response.text}")

        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise GridApiError(f"Request failed: {e}")

    # =========================================================================
    # DEMO DATA - Used when GRID API key is not configured
    # This provides realistic sample data for development and demonstration
    # =========================================================================

    def _get_demo_teams(self) -> List[Team]:
        """Get demo VALORANT teams for development."""
        return [
            Team(
                id="team_sentinels",
                name="Sentinels",
                short_name="SEN",
                region="NA",
                roster=[
                    Player(id="p1", name="TenZ", nickname="TenZ", team_id="team_sentinels", role="Duelist"),
                    Player(id="p2", name="zekken", nickname="zekken", team_id="team_sentinels", role="Flex"),
                    Player(id="p3", name="Sacy", nickname="Sacy", team_id="team_sentinels", role="Initiator"),
                    Player(id="p4", name="pANcada", nickname="pANcada", team_id="team_sentinels", role="Controller"),
                    Player(id="p5", name="johnqt", nickname="johnqt", team_id="team_sentinels", role="IGL"),
                ]
            ),
            Team(
                id="team_fnatic",
                name="Fnatic",
                short_name="FNC",
                region="EMEA",
                roster=[
                    Player(id="p6", name="Derke", nickname="Derke", team_id="team_fnatic", role="Duelist"),
                    Player(id="p7", name="Alfajer", nickname="Alfajer", team_id="team_fnatic", role="Duelist"),
                    Player(id="p8", name="Chronicle", nickname="Chronicle", team_id="team_fnatic", role="Sentinel"),
                    Player(id="p9", name="Boaster", nickname="Boaster", team_id="team_fnatic", role="IGL"),
                    Player(id="p10", name="Enzo", nickname="Enzo", team_id="team_fnatic", role="Controller"),
                ]
            ),
            Team(
                id="team_loud",
                name="LOUD",
                short_name="LOUD",
                region="BR",
                roster=[
                    Player(id="p11", name="aspas", nickname="aspas", team_id="team_loud", role="Duelist"),
                    Player(id="p12", name="Less", nickname="Less", team_id="team_loud", role="Initiator"),
                    Player(id="p13", name="tuyz", nickname="tuyz", team_id="team_loud", role="Controller"),
                    Player(id="p14", name="cauanzin", nickname="cauanzin", team_id="team_loud", role="Sentinel"),
                    Player(id="p15", name="qck", nickname="qck", team_id="team_loud", role="Flex"),
                ]
            ),
            Team(
                id="team_drx",
                name="DRX",
                short_name="DRX",
                region="KR",
                roster=[
                    Player(id="p16", name="MaKo", nickname="MaKo", team_id="team_drx", role="Controller"),
                    Player(id="p17", name="Rb", nickname="Rb", team_id="team_drx", role="Duelist"),
                    Player(id="p18", name="Zest", nickname="Zest", team_id="team_drx", role="Initiator"),
                    Player(id="p19", name="BuZz", nickname="BuZz", team_id="team_drx", role="Flex"),
                    Player(id="p20", name="stax", nickname="stax", team_id="team_drx", role="IGL"),
                ]
            ),
            Team(
                id="team_nrg",
                name="NRG Esports",
                short_name="NRG",
                region="NA",
                roster=[
                    Player(id="p21", name="s0m", nickname="s0m", team_id="team_nrg", role="Duelist"),
                    Player(id="p22", name="FNS", nickname="FNS", team_id="team_nrg", role="IGL"),
                    Player(id="p23", name="ardiis", nickname="ardiis", team_id="team_nrg", role="Flex"),
                    Player(id="p24", name="crashies", nickname="crashies", team_id="team_nrg", role="Initiator"),
                    Player(id="p25", name="Victor", nickname="Victor", team_id="team_nrg", role="Duelist"),
                ]
            ),
            Team(
                id="team_prx",
                name="Paper Rex",
                short_name="PRX",
                region="APAC",
                roster=[
                    Player(id="p26", name="f0rsakeN", nickname="f0rsakeN", team_id="team_prx", role="Duelist"),
                    Player(id="p27", name="Jinggg", nickname="Jinggg", team_id="team_prx", role="Duelist"),
                    Player(id="p28", name="d4v41", nickname="d4v41", team_id="team_prx", role="Initiator"),
                    Player(id="p29", name="Monyet", nickname="Monyet", team_id="team_prx", role="Controller"),
                    Player(id="p30", name="mindfreak", nickname="mindfreak", team_id="team_prx", role="Sentinel"),
                ]
            ),
        ]

    def _generate_demo_matches(self, team: Team, opponent_teams: List[Team], num_matches: int = 10) -> List[Match]:
        """Generate realistic demo match data for a team."""
        import random

        maps = ["Ascent", "Bind", "Haven", "Split", "Icebox", "Breeze", "Lotus", "Sunset"]
        agents_by_role = {
            "Duelist": ["Jett", "Raze", "Reyna", "Neon", "Phoenix"],
            "Controller": ["Omen", "Astra", "Viper", "Brimstone", "Harbor"],
            "Initiator": ["Sova", "Fade", "Skye", "KAY/O", "Breach", "Gekko"],
            "Sentinel": ["Killjoy", "Cypher", "Sage", "Chamber", "Deadlock"],
            "Flex": ["Jett", "Raze", "Sova", "Fade", "Omen", "Viper"],
            "IGL": ["Omen", "Brimstone", "Fade", "Sova", "Astra"],
        }

        matches = []
        base_date = datetime.now()

        for i in range(num_matches):
            opponent = random.choice([t for t in opponent_teams if t.id != team.id])
            match_date = base_date - timedelta(days=random.randint(1, 90))
            best_of = random.choice([3, 5])

            # Generate map results
            maps_to_play = random.sample(maps, k=random.randint(2, min(best_of, 5)))
            map_results = []
            team_a_wins = 0
            team_b_wins = 0

            for map_name in maps_to_play:
                # Generate realistic scores (13-X format with possible overtime)
                winner_score = 13
                loser_score = random.randint(4, 11)
                if random.random() < 0.15:  # 15% chance of overtime
                    winner_score = random.choice([14, 15, 16])
                    loser_score = winner_score - 2

                team_a_won = random.random() < 0.55 if team.region in ["NA", "EMEA"] else random.random() < 0.45

                if team_a_won:
                    team_a_wins += 1
                    map_results.append(MapResult(
                        map_name=map_name,
                        team_a_score=winner_score,
                        team_b_score=loser_score,
                        team_a_side_first=random.choice(["attack", "defense"]),
                        winner_team_id=team.id
                    ))
                else:
                    team_b_wins += 1
                    map_results.append(MapResult(
                        map_name=map_name,
                        team_a_score=loser_score,
                        team_b_score=winner_score,
                        team_a_side_first=random.choice(["attack", "defense"]),
                        winner_team_id=opponent.id
                    ))

            # Generate player stats
            player_stats = []
            agent_picks = []

            for player in team.roster:
                role = player.role or "Flex"
                agent = random.choice(agents_by_role.get(role, agents_by_role["Flex"]))

                kills = random.randint(12, 28)
                deaths = random.randint(10, 22)
                assists = random.randint(3, 12)

                player_stats.append(PlayerMatchStats(
                    player_id=player.id,
                    player_name=player.name,
                    agent=agent,
                    kills=kills,
                    deaths=deaths,
                    assists=assists,
                    acs=random.uniform(180, 320),
                    adr=random.uniform(120, 200),
                    kast=random.uniform(60, 85),
                    first_kills=random.randint(0, 5),
                    first_deaths=random.randint(0, 4),
                    headshot_percentage=random.uniform(15, 35),
                    clutches_won=random.randint(0, 3),
                    clutches_attempted=random.randint(0, 5)
                ))

                for map_result in map_results:
                    agent_picks.append(AgentPick(
                        player_id=player.id,
                        player_name=player.name,
                        agent=agent,
                        map_name=map_result.map_name,
                        match_id=f"match_{i}"
                    ))

            # Add opponent stats too
            for player in opponent.roster:
                role = player.role or "Flex"
                agent = random.choice(agents_by_role.get(role, agents_by_role["Flex"]))

                kills = random.randint(12, 28)
                deaths = random.randint(10, 22)
                assists = random.randint(3, 12)

                player_stats.append(PlayerMatchStats(
                    player_id=player.id,
                    player_name=player.name,
                    agent=agent,
                    kills=kills,
                    deaths=deaths,
                    assists=assists,
                    acs=random.uniform(180, 320),
                    adr=random.uniform(120, 200),
                    kast=random.uniform(60, 85),
                    first_kills=random.randint(0, 5),
                    first_deaths=random.randint(0, 4),
                    headshot_percentage=random.uniform(15, 35),
                    clutches_won=random.randint(0, 3),
                    clutches_attempted=random.randint(0, 5)
                ))

            winner_id = team.id if team_a_wins > team_b_wins else opponent.id

            matches.append(Match(
                id=f"match_{team.short_name}_{i}_{int(match_date.timestamp())}",
                team_a_id=team.id,
                team_b_id=opponent.id,
                team_a_name=team.name,
                team_b_name=opponent.name,
                winner_team_id=winner_id,
                date=match_date,
                tournament_name=random.choice([
                    "VCT Masters", "VCT Champions", "VCT Challengers",
                    "VCT League", "Red Bull Home Ground"
                ]),
                best_of=best_of,
                maps_played=map_results,
                team_a_map_wins=team_a_wins,
                team_b_map_wins=team_b_wins,
                player_stats=player_stats,
                agent_picks=agent_picks
            ))

        return matches

    # =========================================================================
    # PUBLIC API METHODS
    # =========================================================================

    async def get_teams(self, search: str = None) -> List[Team]:
        """
        Fetch available VALORANT teams.

        Args:
            search: Optional search string to filter teams

        Returns:
            List of Team objects
        """
        logger.info(f"Fetching teams (search={search})")

        # For demo/hackathon, use demo data which provides realistic VALORANT teams
        # In production, this would integrate with the full GRID API
        logger.info("Using demo VALORANT team data")
        teams = self._get_demo_teams()
        if search:
            search_lower = search.lower()
            teams = [t for t in teams if search_lower in t.name.lower() or search_lower in t.short_name.lower()]
        return teams


    async def get_team_by_id(self, team_id: str) -> Optional[Team]:
        """
        Fetch a specific team by ID.

        Args:
            team_id: Team identifier

        Returns:
            Team object or None if not found
        """
        logger.info(f"Fetching team: {team_id}")
        teams = self._get_demo_teams()
        return next((t for t in teams if t.id == team_id), None)

    async def get_team_matches(
        self,
        team_id: str,
        time_window_days: int = 90,
        limit: int = 20
    ) -> List[Match]:
        """
        Fetch recent matches for a team.

        Args:
            team_id: Team identifier
            time_window_days: Number of days to look back
            limit: Maximum number of matches to return

        Returns:
            List of Match objects
        """
        logger.info(f"Fetching matches for team {team_id} (last {time_window_days} days)")

        # Use demo data for hackathon demonstration
        teams = self._get_demo_teams()
        team = next((t for t in teams if t.id == team_id), None)
        if team:
            return self._generate_demo_matches(team, teams, num_matches=min(limit, 15))
        return []

    async def get_head_to_head(
        self,
        team_a_id: str,
        team_b_id: str,
        time_window_days: int = 365
    ) -> List[Match]:
        """
        Fetch head-to-head matches between two teams.

        Args:
            team_a_id: First team identifier
            team_b_id: Second team identifier
            time_window_days: Number of days to look back

        Returns:
            List of Match objects where these teams faced each other
        """
        logger.info(f"Fetching head-to-head: {team_a_id} vs {team_b_id}")

        # Use demo data for hackathon demonstration
        teams = self._get_demo_teams()
        team_a = next((t for t in teams if t.id == team_a_id), None)
        team_b = next((t for t in teams if t.id == team_b_id), None)

        if team_a and team_b:
            import random
            h2h_matches = []
            for i in range(random.randint(2, 5)):
                match = self._generate_demo_matches(team_a, [team_b], num_matches=1)[0]
                match.team_b_id = team_b.id
                match.team_b_name = team_b.name
                h2h_matches.append(match)
            return h2h_matches
        return []

    async def fetch_scouting_data(
        self,
        team_a_id: str,
        team_b_id: str,
        time_window_days: int = 90
    ) -> GridDataPackage:
        """
        Fetch complete scouting data package for two teams.

        This is the main method used by the analysis module.
        It fetches all necessary data and packages it for analysis.

        Args:
            team_a_id: Our team identifier
            team_b_id: Opponent team identifier
            time_window_days: Analysis time window

        Returns:
            GridDataPackage with all fetched data
        """
        logger.info(f"=== Fetching Scouting Data Package ===")
        logger.info(f"Team A: {team_a_id}")
        logger.info(f"Team B: {team_b_id}")
        logger.info(f"Time window: {time_window_days} days")

        # Fetch team info
        team_a = await self.get_team_by_id(team_a_id)
        team_b = await self.get_team_by_id(team_b_id)

        if not team_a or not team_b:
            raise GridApiError("Could not find one or both teams")

        # Fetch match history for both teams
        team_a_matches = await self.get_team_matches(team_a_id, time_window_days)
        team_b_matches = await self.get_team_matches(team_b_id, time_window_days)

        # Fetch head-to-head
        h2h_matches = await self.get_head_to_head(team_a_id, team_b_id, time_window_days)

        # Compute team match histories
        team_a_history = self._compute_team_history(team_a, team_a_matches)
        team_b_history = self._compute_team_history(team_b, team_b_matches)

        data_package = GridDataPackage(
            team_a=team_a_history,
            team_b=team_b_history,
            head_to_head_matches=h2h_matches,
            fetch_timestamp=datetime.now(),
            time_window_days=time_window_days,
            data_source="GRID Esports API"
        )

        logger.info(f"=== Scouting Data Package Complete ===")
        logger.info(f"Team A matches: {len(team_a_matches)}")
        logger.info(f"Team B matches: {len(team_b_matches)}")
        logger.info(f"Head-to-head matches: {len(h2h_matches)}")

        return data_package

    def _compute_team_history(self, team: Team, matches: List[Match]) -> TeamMatchHistory:
        """Compute statistics from match history."""
        wins = sum(1 for m in matches if m.winner_team_id == team.id)
        losses = len(matches) - wins
        win_rate = (wins / len(matches) * 100) if matches else 0

        # Compute map statistics
        map_stats = {}
        agent_picks = {}

        for match in matches:
            is_team_a = match.team_a_id == team.id

            for map_result in match.maps_played:
                map_name = map_result.map_name
                if map_name not in map_stats:
                    map_stats[map_name] = {"played": 0, "wins": 0, "rounds_won": 0, "rounds_lost": 0}

                map_stats[map_name]["played"] += 1
                team_won = map_result.winner_team_id == team.id
                if team_won:
                    map_stats[map_name]["wins"] += 1

                if is_team_a:
                    map_stats[map_name]["rounds_won"] += map_result.team_a_score
                    map_stats[map_name]["rounds_lost"] += map_result.team_b_score
                else:
                    map_stats[map_name]["rounds_won"] += map_result.team_b_score
                    map_stats[map_name]["rounds_lost"] += map_result.team_a_score

            # Count agent picks
            for pick in match.agent_picks:
                if pick.player_id in [p.id for p in team.roster]:
                    agent_picks[pick.agent] = agent_picks.get(pick.agent, 0) + 1

        # Calculate win rates per map
        for map_name in map_stats:
            played = map_stats[map_name]["played"]
            wins = map_stats[map_name]["wins"]
            map_stats[map_name]["win_rate"] = (wins / played * 100) if played > 0 else 0

        # Recent form (last 5 matches)
        recent_matches = sorted(matches, key=lambda m: m.date, reverse=True)[:5]
        recent_form = ["W" if m.winner_team_id == team.id else "L" for m in recent_matches]

        return TeamMatchHistory(
            team=team,
            matches=matches,
            total_matches=len(matches),
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            map_stats=map_stats,
            agent_picks=agent_picks,
            recent_form=recent_form
        )
