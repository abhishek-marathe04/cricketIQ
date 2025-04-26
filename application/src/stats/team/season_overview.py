
from stats.common_functions.common_team_stats import run_rate_per_phase
from utils.logger import get_logger
from stats.common_functions.graph_functions import show_table
from stats.load_dataframes import get_ball_by_ball_data, get_matches_data, get_team_name

logger = get_logger()


def season_overview(season_id:int):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    
    season_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['season_id'] == season_id]

    batter_stats = season_stats.groupby('batter').agg(
        total_runs=('batter_runs', 'sum'),
        balls_faced=('batter_runs', 'count')  # assuming each row = 1 ball
    ).reset_index()

    # Calculate Strike Rate
    batter_stats['strike_rate'] = (batter_stats['total_runs'] / batter_stats['balls_faced']) * 100

    # Filter out batters who faced very few balls (optional: like minimum 30 balls)
    batter_stats = batter_stats[batter_stats['balls_faced'] >= 30]

    # Sort by strike rate and runs
    top_batters = batter_stats.sort_values(by=['total_runs'], ascending=[False])
    top_5_batters = top_batters.head(5)

    table = show_table(
        header_values=["Batter", "Runs", "Strike Rate"],
        cell_values=[top_5_batters['batter'], top_5_batters['total_runs'], top_5_batters['strike_rate']],
        title="Top 5 Batters by Strike Rate and Runs"
    )
    run_rate = run_rate_per_phase(season_stats, 'team_batting_name', f"Run Rate per Phase in {season_id} Season")
    run_rate_concedded = run_rate_per_phase(season_stats, 'team_bowling_name', f"Run Rate Concedded per Phase in {season_id} Season")
    return table, [run_rate, run_rate_concedded]