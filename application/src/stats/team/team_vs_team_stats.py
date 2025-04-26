
from utils.logger import get_logger
from stats.common_functions.graph_functions import show_table
from stats.load_dataframes import get_matches_data, get_team_name

logger = get_logger()


def show_team_vs_team_stats(team1_name:str, team2_name:  str):
    matches_data = get_matches_data()

    team1 = get_team_name(team1_name)
    team2 = get_team_name(team2_name)
    # Filter matches where the two teams played against each other
    head_to_head = matches_data[
        ((matches_data['team1_name'] == team1) & (matches_data['team2_name'] == team2)) |
        ((matches_data['team1_name'] == team2) & (matches_data['team2_name'] == team1))
    ]

    # Only keep results with a winner (ignore No Results, Tied without superover etc if needed)
    head_to_head = head_to_head[head_to_head['match_winner_name'].notna()]

    # Now calculate win counts
    team_wins = head_to_head['match_winner_name'].value_counts().to_dict()

    # Prepare final output
    team1_wins = team_wins.get(team1, 0)
    team2_wins = team_wins.get(team2, 0)
    total_matches = len(head_to_head)


    header_values = ["Head-to-Head", f"{team1} Wins", f"{team2} Wins",  "Total Matches Played"]
    cell_values = [[f"{team1} vs {team2}"], [team1_wins], [team2_wins], [total_matches]]
    table = show_table(header_values=header_values, cell_values=cell_values, title=f"Head to Head stats for {team1} vs {team2}")
    return table, []