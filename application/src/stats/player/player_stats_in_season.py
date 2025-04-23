

import pandas as pd
from utils.logger import get_logger
from stats.common_functions.maths_utilities import add_strike_rate_to_df
from stats.common_functions.common_player_stats import get_batter_stats, show_player_average, show_player_strike_rate, get_legal_deliveries
from stats.common_functions.graph_functions import show_line_graph, show_table
from stats.load_dataframes import get_ball_by_ball_data, get_player_name

logger = get_logger()


def show_player_stats_in_season(player_name:str, season: int):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    player_name = get_player_name(player_name)
    season = season
    logger.info(f"Inside show_player_stats_in_season player_name {player_name} season {season}")
    player_stats_in_season = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == player_name) & (ipl_ball_by_ball_stats['season_id'] == season)]

    balls_faced, runs_scored, outs, fours, six, average, strike_rate = get_batter_stats(player_stats_in_season, player_name)

    header_values = ["Player", "Runs Scored", "Balls Faced",  "Outs", "Fours", "Sixes", "Average", "Strike Rate"]
    cell_values = [[player_name], [runs_scored], [balls_faced], [outs], [fours], [six], [average], [strike_rate]]
    table = show_table(header_values=header_values, cell_values=cell_values, title=f"Performance Summary of {player_name} in Season {season}")

    # Player Stats per Phase
    custom_order = ['Powerplay', 'Middle Overs', 'Death Overs']

    players_runs_per_phase = player_stats_in_season.groupby('over_phase')['batter_runs'].sum().reset_index()
    legal_deliveries_faced_by_player = get_legal_deliveries(player_stats_in_season)
    # Set custom order
    players_runs_per_phase['over_phase'] = pd.Categorical(
        players_runs_per_phase['over_phase'],
        categories=custom_order,
        ordered=True
    )

    players_runs_per_phase = players_runs_per_phase.sort_values('over_phase')

    # # Group by phase and count rows
    balls_faced_per_phase = legal_deliveries_faced_by_player.groupby('over_phase').size().reset_index()
    balls_faced_per_phase.columns = ['over_phase','balls_faced']

    player_stats_per_phase = pd.merge(players_runs_per_phase, balls_faced_per_phase, on='over_phase', how='inner')
    add_strike_rate_to_df(player_stats_per_phase)

    player_performance_per_phase_graph = show_line_graph(df=player_stats_per_phase, x='over_phase', y='strike_rate', title='Strike rate per Phase')

    # Player Stats Per Match

    players_runs_per_match = (
        player_stats_in_season
        .groupby(['match_id', 'team_bowling_name'])['batter_runs']
        .sum()
        .reset_index()
    )

    # Add a label column to show on x-axis
    players_runs_per_match['match_vs'] = players_runs_per_match.apply(
        lambda row: f"vs {row['team_bowling_name']} (ID: {row['match_id']})", axis=1
    )

    player_stats_per_match = show_line_graph(
        df=players_runs_per_match,
        x='match_vs',
        y='batter_runs',
        title='Runs Per Match',
    )

    player_avg_graph = show_player_average(player_stats_in_season, 'bowler_type', player_name=player_name, title="Average vs Bowler Type")

    player_strike_rate_graph = show_player_strike_rate(player_stats_in_season, 'bowler_type', 'Strike Rate vs Bowler Type')
    return table, [player_stats_per_match, player_performance_per_phase_graph, player_avg_graph, player_strike_rate_graph]