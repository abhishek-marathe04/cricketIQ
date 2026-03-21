

import pandas as pd
from utils.logger import get_logger
from stats.load_dataframes import get_ball_by_ball_data, get_player_name, get_matches_data, get_team_name, get_teams_data

logger = get_logger()

def calculate_batter_performance_metrics(matchup):
    if matchup.empty:
        return None

    runs = matchup['batter_runs'].sum()
    number_of_fours = (matchup['batter_runs'] == 4).sum()
    number_of_sixes = (matchup['batter_runs'] == 6).sum()
    balls = len(matchup)
    outs = matchup['player_out'].count()
    batter_average = (runs / outs) if outs > 0 else None
    strike_rate = (runs / balls) * 100 if balls > 0 else 0
    boundry_percentage = (((number_of_fours * 4) + (number_of_sixes * 6)) / runs) * 100 if runs > 0 else 0

    impact = ((runs / outs + 1) * (strike_rate / 100)) if outs > 0 else None

    return {
        "boundary_percentage": float(round(boundry_percentage, 2)),
        "average": float(round(batter_average, 2)) if batter_average is not None else None,
        "strike_rate": float(round(strike_rate, 2)),
        "impact_score": float(round(impact, 2)) if impact is not None else None
    }

def batter_vs_bowler_stats(batter, bowler):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    matchup = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == batter) & (ipl_ball_by_ball_stats['bowler'] == bowler)]
    if matchup.empty:
        return {"type": "batter_vs_bowler_stats", "batter": batter, "bowler": bowler, "stats": None, "message": "No historical data available"}
    stats = {
        "type": "batter_vs_bowler_stats",
        "batter": batter,
        "bowler": bowler,
        "stats": calculate_batter_performance_metrics(matchup)
    }
    return stats

def batter_vs_team_stats(batter, team):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    teams_data = get_teams_data()
    team_id = teams_data[teams_data['alias_name'] == team]['team_id'].item()
    matchup = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == batter) & (ipl_ball_by_ball_stats['team_bowling'] == team_id)]
    if matchup.empty:
        return {"type": "batter_vs_team_stats", "batter": batter, "opposition_team": team, "stats": None, "message": "No historical data available"}
    stats = {
        "type": "batter_vs_team_stats",
        "batter": batter,
        "opposition_team": team,
        "stats": calculate_batter_performance_metrics(matchup)
    }
    return stats

def batter_at_venue_stats(batter, city):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    ipl_matches_stats = get_matches_data()
    selected_matches = ipl_matches_stats[ipl_matches_stats['city'] == city]['match_id']
    matchup = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == batter) & ipl_ball_by_ball_stats['match_id'].isin(selected_matches)]
    if matchup.empty:
        return {"type": "batter_at_venue_stats", "batter": batter, "city": city, "stats": None, "message": "No historical data available"}
    stats = {
        "type": "batter_at_venue_stats",
        "batter": batter,
        "city": city,
        "stats": calculate_batter_performance_metrics(matchup)
    }
    return stats


def batter_recent_form_stats(batter, num_matches=5):
    ipl_ball_by_ball_stats = get_ball_by_ball_data()
    ipl_matches_stats = get_matches_data()

    batter_matches = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['batter'] == batter]['match_id'].unique()
    if len(batter_matches) == 0:
        return {"type": "batter_recent_form", "batter": batter, "matches_considered": 0, "stats": None, "message": "No historical data available"}

    recent_matches = (
        ipl_matches_stats[ipl_matches_stats['match_id'].isin(batter_matches)]
        .sort_values('match_date', ascending=False)
        .head(num_matches)
    )

    recent_match_ids = recent_matches['match_id'].tolist()
    matchup = ipl_ball_by_ball_stats[
        (ipl_ball_by_ball_stats['batter'] == batter) &
        (ipl_ball_by_ball_stats['match_id'].isin(recent_match_ids))
    ]

    return {
        "type": "batter_recent_form",
        "batter": batter,
        "matches_considered": len(recent_match_ids),
        "stats": calculate_batter_performance_metrics(matchup)
    }