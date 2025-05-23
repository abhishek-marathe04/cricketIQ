import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from collections import defaultdict

from stats.common_functions.custom_exceptions import AmbiguousPlayerNameError, NoPlayerFoundError

# Set the root directory if needed for relative paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
ipl_teams_path = os.path.join(ROOT_DIR, "ipl-dataset-2008-to-2025/teams_data.csv")
ipl_teams_alias_path = os.path.join(ROOT_DIR, "ipl-dataset-2008-to-2025/team_aliases.csv")
ipl_matches_path = os.path.join(ROOT_DIR, "ipl-dataset-2008-to-2025/ipl_matches_data.csv")
ipl_players_path = os.path.join(ROOT_DIR, "ipl-dataset-2008-to-2025/players-data-updated.csv")
ipl_ball_by_ball_path = os.path.join(ROOT_DIR, "ipl-dataset-2008-to-2025/ball_by_ball_data.csv")

def categorize_over(over):
    if over < 6:
        return 'Powerplay'
    elif over < 16:
        return 'Middle Overs'
    else:
        return 'Death Overs'

def load_data():
    """
    Load all required datasets into DataFrames.
    """
    teams_df = pd.read_csv(ipl_teams_path)
    matches_df = pd.read_csv(ipl_matches_path)
    ball_by_ball_df = pd.read_csv(ipl_ball_by_ball_path)
    
    return teams_df, matches_df, ball_by_ball_df

def process_ball_by_ball_data():
    """
    Process datasets and combine them for easy access.
    """
    # Load the data
    teams_df, matches_df, ball_by_ball_df = load_data()
    
    ball_by_ball_df = ball_by_ball_df.merge(
        teams_df[['team_id', 'team_name']],
        left_on='team_batting',
        right_on='team_id',
        how='left'
    ).rename(columns={'team_name': 'team_batting_name'}).drop(columns='team_id')

    ball_by_ball_df = ball_by_ball_df.merge(
        teams_df[['team_id', 'team_name']],
        left_on='team_bowling',
        right_on='team_id',
        how='left'
    ).rename(columns={'team_name': 'team_bowling_name'}).drop(columns='team_id')

    ball_by_ball_df = ball_by_ball_df.merge(
        matches_df[['match_id', 'city']],
        on='match_id',
        how='left'  # or 'inner' if you only want matches present in both
    )


    ball_by_ball_df['over_phase'] = ball_by_ball_df['over_number'].apply(categorize_over)
    
    # Returning combined and processed DataFrame
    return ball_by_ball_df


def process_matches_data():

    teams_df, matches_df, ball_by_ball_df = load_data()

    matches_data = matches_df.merge(
        teams_df[['team_id', 'team_name']],
        left_on='team1',
        right_on='team_id',
        how='left'
    ).rename(columns={'team_name': 'team1_name'}).drop(columns='team_id')

    matches_data = matches_data.merge(
        teams_df[['team_id', 'team_name']],
        left_on='team2',
        right_on='team_id',
        how='left'
    ).rename(columns={'team_name': 'team2_name'}).drop(columns='team_id')

    matches_data = matches_data.merge(
        teams_df[['team_id', 'team_name']],
        left_on='match_winner',
        right_on='team_id',
        how='left'
    ).rename(columns={'team_name': 'match_winner_name'}).drop(columns='team_id')

    return matches_data


def process_players_mapping():
    players_map = defaultdict(list)
    players_df = pd.read_csv(ipl_players_path)

    for _, row in players_df.iterrows():
        short_name = row['player_name']
        full_name = row['player_full_name']
        
        parts = full_name.split()
        if len(parts) >= 2:
            first, last = parts[0], parts[-1]
            initials = ''.join([p[0] for p in parts])
            simplified_full = f"{first} {last}".lower()
            
            players_map[first.lower()].append(short_name)
            players_map[last.lower()].append(short_name)
            players_map[initials.lower()].append(short_name)
            players_map[short_name.lower()].append(short_name)
            if short_name.lower() != simplified_full:
                players_map[simplified_full].append(short_name)

    return players_map

def process_team_names():
    ipl_teams_alias_df = pd.read_csv(ipl_teams_alias_path)
    teams_df = pd.read_csv(ipl_teams_path)

    ipl_teams_alias_df = ipl_teams_alias_df.merge(
        teams_df[['team_id', 'team_name']],
        on='team_id',
        how='left'
    )

    return ipl_teams_alias_df


# Use the function to export the data when needed
ipl_ball_by_ball_data = process_ball_by_ball_data()

players_mapping = process_players_mapping()

teams_mapping = process_team_names()

ipl_matches_data = process_matches_data()

# For exporting processed data to use in other files
def get_ball_by_ball_data():
    return ipl_ball_by_ball_data

def get_matches_data():
    return ipl_matches_data

def get_player_name(user_input):
    key = user_input.strip().lower()
    matches = players_mapping.get(key)
    
    if matches:
        if len(matches) == 1:
            return matches[0]
        else:
            raise AmbiguousPlayerNameError(f"Multiple players found for '{key}': {matches}. Please search with full name")
    else:
        raise NoPlayerFoundError(f"No players found with name '{key}': Please try another keyword")

def get_team_name(user_input):
    alias_input_lower = user_input.lower()
    
    match = teams_mapping[teams_mapping['alias_name'].str.lower() == alias_input_lower]
    if not match.empty:
        return match.iloc[0]['team_name']
    return None  # or raise an error or fallback to alias_input