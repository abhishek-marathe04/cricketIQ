import pandas as pd
from utils.logger import get_logger
from stats.load_dataframes import get_ball_by_ball_data, get_player_name, get_matches_data, get_teams_data

logger = get_logger()

def calculate_bowler_performance_metrics(matchup):
    number_of_balls_bowled = len(matchup)
    number_of_no_balls = matchup['is_no_ball'].sum()
    number_of_wide_balls = matchup['is_wide_ball'].sum()
    batter_runs = matchup['batter_runs'].sum()
    no_ball_runs = matchup['no_ball_runs'].sum()
    wide_ball_runs = matchup['wide_ball_runs'].sum()
    wickets = matchup['player_out'].count() # or however your 'out' column is named
    runs_concedded = batter_runs + no_ball_runs + wide_ball_runs
    
    legal_balls_bowled = number_of_balls_bowled - number_of_no_balls - number_of_wide_balls
    economy_rate = (runs_concedded / legal_balls_bowled) * 6
    bowler_average = runs_concedded / wickets
    strike_rate = legal_balls_bowled / wickets

    # Use outs + 1 to avoid division by zero
    # impact = (wickets+1) * 100 / (runs_concedded + number_of_balls_bowled)
    impact = (wickets) + (number_of_balls_bowled - runs_concedded) / (number_of_balls_bowled/6)
    
    print(f"number_of_balls_bowled : {number_of_balls_bowled} ")
    print(f"wickets : {wickets} ")
    print(f"runs_concedded : {runs_concedded} ")
    return {
        "economy": float(round(economy_rate, 2)),
        "average": float(round(bowler_average, 2)),
        "strike_rate": strike_rate,
        "impact_score": float(round(impact, 2))
    }

def bowler_vs_team_stats(bowler, team):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    teams_data = get_teams_data()
    team_id = teams_data[teams_data['alias_name'] == team]['team_id'].item()
    matchup = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['bowler'] == bowler) & (ipl_ball_by_ball_stats['team_batting'] == team_id)]
    if matchup.empty:
        return {"type": "bowler_vs_team_stats", "bowler": bowler, "opposition_team": team, "stats": None, "message": "No historical data available"}
    return {
        "type": "bowler_vs_team_stats",
        "bowler": bowler,
        "opposition_team": team,
        "stats": calculate_bowler_performance_metrics(matchup)
    }

def bowler_at_venue_stats(bowler, city):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    ipl_matches_stats = get_matches_data()
    selected_matches = ipl_matches_stats[ipl_matches_stats['city'] == city]['match_id']
    matchup = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['bowler'] == bowler)
                                     & ipl_ball_by_ball_stats['match_id'].isin(selected_matches)]
    if matchup.empty:
        return {"type": "bowler_at_venue_stats", "bowler": bowler, "city": city, "stats": None, "message": "No historical data available"}
    return {
        "type": "bowler_at_venue_stats",
        "bowler": bowler,
        "city": city,
        "stats": calculate_bowler_performance_metrics(matchup)
    }