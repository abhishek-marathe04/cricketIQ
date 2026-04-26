from typing import Optional
import pandas as pd
from utils.logger import get_logger
from stats.common_functions.maths_utilities import get_legal_deliveries
from stats.common_functions.graph_functions import show_bar_graph, show_line_graph, show_table
from stats.load_dataframes import get_ball_by_ball_data, get_player_name, get_team_name

logger = get_logger()


def _get_bowler_summary_stats(df):
    legal_balls = get_legal_deliveries(df)
    balls_bowled = len(legal_balls)
    wickets = int(df['is_wicket'].sum())
    runs_conceded = int(
        df['batter_runs'].sum() +
        df['no_ball_runs'].sum() +
        df['wide_ball_runs'].sum()
    )
    economy = round((runs_conceded / balls_bowled) * 6, 2) if balls_bowled > 0 else 0.0
    average = round(runs_conceded / wickets, 2) if wickets > 0 else float('inf')
    strike_rate = round(balls_bowled / wickets, 2) if wickets > 0 else float('inf')
    dot_balls = int(legal_balls[legal_balls['total_runs'] == 0].shape[0])

    return balls_bowled, wickets, runs_conceded, economy, average, strike_rate, dot_balls


def show_bowler_stats(
    bowler_name: str,
    opponent_team_name: Optional[str] = None,
    city_name: Optional[str] = None,
    season: Optional[int] = None,
    batter_name: Optional[str] = None,
    batter_type: Optional[str] = None,
):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()

    bowler_name = get_player_name(bowler_name) if bowler_name else None
    batter_resolved = get_player_name(batter_name) if batter_name else None
    opposite_team = get_team_name(opponent_team_name) if opponent_team_name else None

    mask = (ipl_ball_by_ball_stats['bowler'] == bowler_name)

    if opposite_team:
        mask &= (ipl_ball_by_ball_stats['team_batting_name'] == opposite_team)

    if city_name:
        mask &= (ipl_ball_by_ball_stats['city'] == city_name)

    if season:
        mask &= (ipl_ball_by_ball_stats['season_id'] == season)

    if batter_resolved:
        mask &= (ipl_ball_by_ball_stats['batter'] == batter_resolved)

    if batter_type:
        mask &= (ipl_ball_by_ball_stats['batsman_type'] == batter_type)

    bowler_df = ipl_ball_by_ball_stats[mask]

    group_by_field = 'match_vs' if season else 'season_id'
    group_by_title = 'Match' if season else 'Season'

    if season:
        bowler_df = bowler_df.copy()
        bowler_df['match_vs'] = bowler_df.apply(
            lambda row: f"vs {row['team_batting_name']} (ID: {row['match_id']})", axis=1
        )

    balls_bowled, wickets, runs_conceded, economy, average, strike_rate, dot_balls = _get_bowler_summary_stats(bowler_df)

    logger.info(f"show_bowler_stats: {bowler_name} | wickets={wickets} economy={economy}")

    header_values = ["Player", "Wickets", "Balls Bowled", "Runs Conceded", "Economy", "Average", "Strike Rate", "Dot Balls"]
    cell_values = [[bowler_name], [wickets], [balls_bowled], [runs_conceded], [economy], [average], [strike_rate], [dot_balls]]
    table = show_table(header_values=header_values, cell_values=cell_values, title=f"Bowling Summary: {bowler_name}")

    summary_df = pd.DataFrame({
        "Player": [bowler_name],
        "Wickets": [wickets],
        "Balls Bowled": [balls_bowled],
        "Runs Conceded": [runs_conceded],
        "Economy": [economy],
        "Average": [average],
        "Strike Rate": [strike_rate],
        "Dot Balls": [dot_balls],
    })

    # Wickets per season/match
    legal_balls_df = get_legal_deliveries(bowler_df)
    wickets_per_group = (
        bowler_df[bowler_df['is_wicket'] == True]
        .groupby(group_by_field)
        .size()
        .reset_index(name='wickets')
    )
    wickets_graph = show_bar_graph(df=wickets_per_group, x=group_by_field, y='wickets', title=f'Wickets Per {group_by_title}')

    # Economy per season/match
    runs_per_group = (
        bowler_df.groupby(group_by_field)
        .apply(lambda g: (g['batter_runs'].sum() + g['no_ball_runs'].sum() + g['wide_ball_runs'].sum()))
        .reset_index(name='runs_conceded')
    )
    balls_per_group = (
        legal_balls_df.groupby(group_by_field)
        .size()
        .reset_index(name='balls')
    )
    economy_df = pd.merge(runs_per_group, balls_per_group, on=group_by_field, how='inner')
    economy_df['economy'] = (economy_df['runs_conceded'] / economy_df['balls'] * 6).round(2)
    economy_graph = show_line_graph(df=economy_df, x=group_by_field, y='economy', title=f'Economy Per {group_by_title}')

    return table, [wickets_graph, economy_graph], summary_df
