

from typing import Optional
import pandas as pd
from utils.logger import get_logger
from stats.common_functions.maths_utilities import add_strike_rate_to_df
from stats.common_functions.common_player_stats import get_batter_stats, show_player_average, show_player_strike_rate, get_legal_deliveries, show_runs_per_season
from stats.common_functions.graph_functions import show_line_graph, show_table
from stats.load_dataframes import get_ball_by_ball_data, get_player_name, get_team_name

logger = get_logger()


def show_batter_stats(batter_name:str, opponent_team_name:  Optional[str], city_name: Optional[str], season: Optional[int]):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    batter_name = get_player_name(batter_name) if batter_name else None
    opposite_team = get_team_name(opponent_team_name) if opponent_team_name else None

    # Base filter: player vs team
    mask = (
        (ipl_ball_by_ball_stats['batter'] == batter_name) 
    )

    if opponent_team_name:
        mask &= (ipl_ball_by_ball_stats['team_bowling_name'] == opposite_team)

    # Optionally add city filter if city_name is provided
    if city_name:  # Ensure it's not None or empty
        mask &= (ipl_ball_by_ball_stats['city'] == city_name)

    if season:
        mask &= (ipl_ball_by_ball_stats['season_id'] == season)

    logger.info(f"Inside show_batter_stats batter_name {batter_name} opponent_team_name {opponent_team_name} city_name {city_name}")

    player_stats_vs_particular_team = ipl_ball_by_ball_stats[mask]

    balls_faced, runs_scored, outs, fours, six, average, strike_rate = get_batter_stats(player_stats_vs_particular_team, batter_name)

    header_values = ["Player", "Runs Scored", "Balls Faced",  "Outs", "Fours", "Sixes", "Average", "Strike Rate"]
    cell_values = [[batter_name], [runs_scored], [balls_faced], [outs], [fours], [six], [average], [strike_rate]]
    table = show_table(header_values=header_values, cell_values=cell_values, title=f"Performance Summary of {batter_name} vs {opponent_team_name}")
    
    players_runs_per_season = show_runs_per_season(player_stats_vs_particular_team)

    strike_rate_graph = show_player_strike_rate(player_stats_vs_particular_team, 'season_id', 'Strike Rate Per Season')
    average_per_season = show_player_average(player_stats_vs_particular_team, 'season_id', player_name=batter_name, title="Average Per Season")
    return table, [players_runs_per_season, strike_rate_graph, average_per_season]