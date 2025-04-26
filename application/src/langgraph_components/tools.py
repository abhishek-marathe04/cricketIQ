from typing import Optional
from stats.team.season_overview import season_overview
from stats.team.team_vs_team_stats import show_team_vs_team_stats
from stats.player.player_stats_vs_particular_team import show_batter_stats_vs_team
from stats.player.player_stats_vs_bowler import show_batter_stats_vs_bowler
from utils.logger import get_logger
from stats.player.player_stats_vs_bowler_type import show_player_stats_vs_bowler_type
from stats.player.player_stats_in_season import show_player_stats_in_season
from langchain_core.tools import tool

logger = get_logger()
# Tool (could also be agent tool)
@tool(description="Fetches Player stats data for a given Season.")
def call_player_stats_per_season(player_name: str, season: int):
    table, graph = show_player_stats_in_season(player_name=player_name, season=season)
    logger.info(f'Inside call_player_stats_per_season  : {table}')
    return table, graph # placeholder


# Tool (could also be agent tool)
@tool(description="Fetches Player stats data vs Bowler Type")
def call_player_stats_vs_bowler_type(player_name: str, bowler_type: str):
    table, graph = show_player_stats_vs_bowler_type(player_name=player_name, input_bowler_type=bowler_type)
    logger.info(f'Inside call_player_stats_vs_bowler_type  : {table}')
    return table, graph # placeholder


# Tool (could also be agent tool)
@tool(description="Fetches Batter stats data vs Bowler")
def call_batter_stats_vs_bowler(batter_name: str, bowler_name: str):
    table, graph = show_batter_stats_vs_bowler(batter_name=batter_name, bowler_name=bowler_name)
    logger.info(f'Inside call_batter_stats_vs_bowler  : {table}')
    return table, graph # placeholder


# Tool (could also be agent tool)
@tool(description="Fetches Batter stats data vs team")
def call_batter_stats_vs_team(batter_name: str, opponent_team_name: Optional[str], city_name: Optional[str]):
    table, graph = show_batter_stats_vs_team(batter_name=batter_name, opponent_team_name=opponent_team_name, city_name=city_name)
    logger.info(f'Inside call_batter_stats_vs_team  : {table}')
    return table, graph # placeholder


# Tool (could also be agent tool)
@tool(description="Fetches Team vs Team stats")
def call_team_vs_team_stats(team1_name: str, team2_name: str):
    table, graph = show_team_vs_team_stats(team1_name=team1_name, team2_name=team2_name)
    logger.info(f'Inside call_team_vs_team_stats  : {table}')
    return table, graph # placeholder

# Tool (could also be agent tool)
@tool(description="Fetches Particular Season Overview")
def call_season_overview(season: int):
    table, graph = season_overview(season_id=season)
    logger.info(f'Inside call_season_overview  : {table}')
    return table, graph # placeholder
