

import pandas as pd
from utils.logger import get_logger
from stats.common_functions.maths_utilities import add_strike_rate_to_df
from stats.common_functions.common_player_stats import get_batter_stats, show_player_average, show_player_strike_rate, get_legal_deliveries
from stats.common_functions.graph_functions import show_line_graph, show_table
from stats.load_dataframes import get_ball_by_ball_data, get_player_name

logger = get_logger()


def show_batter_stats_vs_bowler(batter_name:str, bowler_name: str):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    batter_name = get_player_name(batter_name)
    bowler_name = get_player_name(bowler_name)

    logger.info(f"Inside show_batter_stats_vs_bowler batter_name {batter_name} bowler_name {bowler_name}")

    player_stats_vs_particular_bowler = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == batter_name) & (ipl_ball_by_ball_stats['bowler'] == bowler_name)]

    balls_faced, runs_scored, outs, fours, six, average, strike_rate = get_batter_stats(player_stats_vs_particular_bowler, batter_name)

    header_values = ["Player", "Runs Scored", "Balls Faced",  "Outs", "Fours", "Sixes", "Average", "Strike Rate"]
    cell_values = [[batter_name], [runs_scored], [balls_faced], [outs], [fours], [six], [average], [strike_rate]]
    table = show_table(header_values=header_values, cell_values=cell_values, title=f"Performance Summary of {batter_name} vs {bowler_name}")

    players_runs_per_season_vs_bowler = (
        player_stats_vs_particular_bowler
        .groupby(['season_id'])['batter_runs']
        .sum()
        .reset_index()
    )

    player_stats_per_season = show_line_graph(
        df=players_runs_per_season_vs_bowler,
        x='season_id',
        y='batter_runs',
        title='Runs Per Season',
    )

    strike_rate_graph = show_player_strike_rate(player_stats_vs_particular_bowler, 'season_id', 'Strike Rate Per Season')
    return table, [player_stats_per_season, strike_rate_graph]