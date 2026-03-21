from utils.logger import get_logger
from stats.player.player_stats_in_season import show_player_stats_in_season
from stats.metrics.batter_metrics import batter_vs_bowler_stats, batter_vs_team_stats, batter_at_venue_stats
from stats.metrics.bowler_metrics import bowler_vs_team_stats, bowler_at_venue_stats
from langchain_core.tools import tool

logger = get_logger()

@tool(description="Fetches Player stats data for a given Season.")
def call_player_stats_per_season(player_name: str, season: int):
    table, graph = show_player_stats_in_season(player_name=player_name, season=season)
    logger.info(f'Inside call_player_stats_per_season  : {table}')
    return table, graph


@tool(description="Fetches batter performance metrics (average, strike rate, boundary %, impact score) against a specific bowler.")
def get_batter_vs_bowler_stats(batter: str, bowler: str) -> dict:
    logger.info(f"get_batter_vs_bowler_stats: batter={batter}, bowler={bowler}")
    return batter_vs_bowler_stats(batter=batter, bowler=bowler)


@tool(description="Fetches batter performance metrics (average, strike rate, boundary %, impact score) against a specific opposition team.")
def get_batter_vs_team_stats(batter: str, team: str) -> dict:
    logger.info(f"get_batter_vs_team_stats: batter={batter}, team={team}")
    return batter_vs_team_stats(batter=batter, team=team)


@tool(description="Fetches batter performance metrics (average, strike rate, boundary %, impact score) at a specific city/venue.")
def get_batter_at_venue_stats(batter: str, city: str) -> dict:
    logger.info(f"get_batter_at_venue_stats: batter={batter}, city={city}")
    return batter_at_venue_stats(batter=batter, city=city)


@tool(description="Fetches bowler performance metrics (economy, average, strike rate, impact score) against a specific batting team.")
def get_bowler_vs_team_stats(bowler: str, team: str) -> dict:
    logger.info(f"get_bowler_vs_team_stats: bowler={bowler}, team={team}")
    return bowler_vs_team_stats(bowler=bowler, team=team)


@tool(description="Fetches bowler performance metrics (economy, average, strike rate, impact score) at a specific city/venue.")
def get_bowler_at_venue_stats(bowler: str, city: str) -> dict:
    logger.info(f"get_bowler_at_venue_stats: bowler={bowler}, city={city}")
    return bowler_at_venue_stats(bowler=bowler, city=city)
