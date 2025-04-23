

import pandas as pd
from stats.common_functions.bowler_type_dictionaries import resolve_bowler_type
from stats.common_functions.maths_utilities import add_strike_rate_to_df
from stats.common_functions.common_player_stats import get_batter_stats, show_player_average, show_player_strike_rate, get_legal_deliveries, show_runs_per_season
from stats.common_functions.graph_functions import show_line_graph, show_table
from stats.load_dataframes import get_ball_by_ball_data, get_player_name
from utils.logger import get_logger

logger = get_logger()

def show_player_stats_vs_bowler_type(player_name:str, input_bowler_type: str):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()

    player_name = get_player_name(player_name)
    bolwer_type_in_query = resolve_bowler_type(input_bowler_type)

    logger.info(f"Inside show_player_stats_vs_bowler_type: player_name {player_name}, bowler_type {bolwer_type_in_query}")
    # bowler_type_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['Team'].isin(team_list)]
    player_stats_vs_particular_bowler_type = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == player_name)]
    # player_stats_vs_particular_bowler_type.head()
    player_stats_vs_particular_bowler_type = player_stats_vs_particular_bowler_type[player_stats_vs_particular_bowler_type['bowler_type'].isin(bolwer_type_in_query)]

    balls_faced, runs_scored, outs, fours, six, average, strike_rate = get_batter_stats(player_stats_vs_particular_bowler_type, player_name)

    header_values = ["Player", "Runs Scored", "Balls Faced",  "Outs", "Fours", "Sixes", "Average", "Strike Rate"]
    cell_values = [[player_name], [runs_scored], [balls_faced], [outs], [fours], [six], [average], [strike_rate]]
    table = show_table(header_values=header_values, cell_values=cell_values, title=f"Performance Summary of {player_name} aginst {input_bowler_type}")

    player_runs_per_season = show_runs_per_season(player_stats_vs_particular_bowler_type)
    player_strike_rate_vs_bowler_type = show_player_strike_rate(player_stats_vs_particular_bowler_type, 'season_id', 'Strike Rate Per Season')
    player_average_vs_bowler_type = show_player_average(player_stats_vs_particular_bowler_type, 'season_id', player_name=player_name, title=f"Average Per Season Against {input_bowler_type}")
    return table, [player_runs_per_season, player_strike_rate_vs_bowler_type, player_average_vs_bowler_type]