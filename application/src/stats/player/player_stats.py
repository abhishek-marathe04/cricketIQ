

from typing import Optional
import pandas as pd
from stats.common_functions.bowler_type_dictionaries import resolve_bowler_type
from utils.logger import get_logger
from stats.common_functions.maths_utilities import add_strike_rate_to_df
from stats.common_functions.common_player_stats import get_batter_stats, show_player_average, show_player_strike_rate, get_legal_deliveries, show_runs, show_runs_per_season
from stats.common_functions.graph_functions import show_line_graph, show_table
from stats.load_dataframes import get_ball_by_ball_data, get_player_name, get_team_name

logger = get_logger()


def show_batter_stats(batter_name:str, opponent_team_name:  Optional[str], city_name: Optional[str], season: Optional[int], bowler_name: Optional[str], bowler_type: Optional[str]):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    batter_name = get_player_name(batter_name) if batter_name else None
    bowler_name = get_player_name(bowler_name) if bowler_name else None
    opposite_team = get_team_name(opponent_team_name) if opponent_team_name else None
    bolwer_type_in_query = resolve_bowler_type(bowler_type) if bowler_type else None

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

        
    
    if bowler_name:
        mask &= (ipl_ball_by_ball_stats['bowler'] == bowler_name)

    if bolwer_type_in_query:
        mask &= (ipl_ball_by_ball_stats['bowler_type'].isin(bolwer_type_in_query))

    group_by_field = 'match_vs' if season else 'season_id'
    group_by_field_2 = 'bowler_type' if season else 'season_id'
    group_by_title_2 = 'Bowler Type' if season else 'season_id'
    group_by_title = 'Match' if season else 'Season'

    logger.info(f"Inside show_batter_stats batter_name {batter_name} opponent_team_name {opponent_team_name} city_name {city_name}")

    player_stats = ipl_ball_by_ball_stats[mask]

    if season:
        player_stats['match_vs'] = player_stats.apply(
            lambda row: f"vs {row['team_bowling_name']} (ID: {row['match_id']})", axis=1
        )

    balls_faced, runs_scored, outs, fours, six, average, strike_rate = get_batter_stats(player_stats, batter_name)

    header_values = ["Player", "Runs Scored", "Balls Faced",  "Outs", "Fours", "Sixes", "Average", "Strike Rate"]
    cell_values = [[batter_name], [runs_scored], [balls_faced], [outs], [fours], [six], [average], [strike_rate]]
    table = show_table(header_values=header_values, cell_values=cell_values, title=f"Performance Summary of {batter_name}")
    
    players_runs_per_season = show_runs(player_stats, group_by_field=group_by_field, group_by_title=group_by_title)

    strike_rate_graph = show_player_strike_rate(player_stats, group_by_field_2, f'Strike Rate Per {group_by_title_2}')
    average_per_season = show_player_average(player_stats, group_by_field_2, player_name=batter_name, title=f"Average Per {group_by_title_2}")
    return table, [players_runs_per_season, strike_rate_graph, average_per_season]