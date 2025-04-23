# %%
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import plotly.express as px

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

# %%
ipl_ball_by_ball_stats = pd.read_csv('/kaggle/input/ipl-dataset-2008-to-2025/ball_by_ball_data.csv')
ipl_teams = pd.read_csv('/kaggle/input/ipl-dataset-2008-to-2025/teams_data.csv')
matches_data = pd.read_csv('/kaggle/input/ipl-dataset-2008-to-2025/ipl_matches_data.csv')
players_data = pd.read_csv('/kaggle/input/ipl-dataset-2008-to-2025/players-data-updated.csv')

# %%
# Merging with ipl_teams to get team names

ipl_ball_by_ball_stats = ipl_ball_by_ball_stats.merge(
    ipl_teams[['team_id', 'team_name']],
    left_on='team_batting',
    right_on='team_id',
    how='left'
).rename(columns={'team_name': 'team_batting_name'}).drop(columns='team_id')

ipl_ball_by_ball_stats = ipl_ball_by_ball_stats.merge(
    ipl_teams[['team_id', 'team_name']],
    left_on='team_bowling',
    right_on='team_id',
    how='left'
).rename(columns={'team_name': 'team_bowling_name'}).drop(columns='team_id')

# %%
ipl_ball_by_ball_stats.head()

# %%
ipl_teams.head()

# %%
matches_data.head()

# %%
def categorize_over(over):
    if over < 6:
        return 'Powerplay'
    elif over < 16:
        return 'Middle Overs'
    else:
        return 'Death Overs'


ipl_ball_by_ball_stats['over_phase'] = ipl_ball_by_ball_stats['over_number'].apply(categorize_over)
ipl_ball_by_ball_stats.head()

# %%
# Common functions

def get_legal_deliveries(df):
    return df[
        (df['is_wide_ball'] == False) & 
        (df['is_no_ball'] == False)
    ]

def get_number_of_outs(df, player_name):
    return len(df[(df['is_wicket'] == True) & (df['player_out'] == player_name)])

def get_number_of_fours(df):
    return len(df[(df['batter_runs'] == 4)])


def get_number_of_six(df):
    return len(df[(df['batter_runs'] == 6)])

def get_average(runs_scored, outs):
    return round((runs_scored / outs), 2)

def get_strike_rate(runs_scored, balls_faced):
    return round((runs_scored / balls_faced) * 100, 2)

def add_strike_rate_to_df(df):
    df['strike_rate'] = round((df['batter_runs'] / df['balls_faced']) * 100, 2)
    return

def add_average_to_df(df):
    df['average'] = df.apply(
        lambda row: round(row['batter_runs'] / row['out'], 2) if row['out'] > 0 else 0,
        axis=1
    )
    return

def get_wicket_stats(df, player_name):
    wickets_df = df[(df['is_wicket'] == True) & (df['player_out'] == player_name)]
    return wickets_df

# %%
def get_batter_stats(df, player_name):
    legal_deliveries_faced_by_player = get_legal_deliveries(df)

    balls_faced = len(legal_deliveries_faced_by_player)
    runs_scored = df['batter_runs'].sum()
    outs = get_number_of_outs(df, player_name)
    fours = get_number_of_fours(df)
    six = get_number_of_six(df)
    average = get_average(runs_scored, outs)
    strike_rate = get_strike_rate(runs_scored, balls_faced)

    return balls_faced, runs_scored, outs, fours, six, average, strike_rate


def show_player_strike_rate(df, group_by_field, title):
    legal_deliveries_faced_by_player = get_legal_deliveries(df)
    df_runs = df.groupby(group_by_field)['batter_runs'].sum().reset_index()
    df_ball_faced = legal_deliveries_faced_by_player.groupby(group_by_field).size().reset_index()
    df_ball_faced.columns = [group_by_field,'balls_faced']
    
    df_strike_rate = pd.merge(df_runs, df_ball_faced, on=group_by_field, how='inner')
    add_strike_rate_to_df(df_strike_rate)
    
    df_strike_rate = df_strike_rate.sort_values(by='strike_rate', ascending=False)
    
    show_bar_graph(df=df_strike_rate, x=group_by_field, y='strike_rate', title=title)

def show_player_average(df, group_by_field, player_name, title):
    
    df_runs = df.groupby(group_by_field)['batter_runs'].sum().reset_index()
    wicket_stats = get_wicket_stats(df, player_name)

    player_out_per_group = wicket_stats.groupby(group_by_field).size().reset_index()
    player_out_per_group.columns = [group_by_field,'out']
    
    df_avg = pd.merge(df_runs, player_out_per_group, on=group_by_field, how='inner')
    df_avg['average'] = df_avg.apply(
        lambda row: round(row['batter_runs'] / row['out'], 2) if row['out'] > 0 else np.inf,
        axis=1
    )
    
    df_avg = df_avg.sort_values(by='average', ascending=False)
    show_bar_graph(df=df_avg, x=group_by_field, y='average', title=title)



# %%

import plotly.graph_objects as go
# Common Graph functions

def show_line_graph(df, x, y, title):   
    fig = px.line(df, x=x, y=y, title=title, markers=True )
    fig.show()


def show_bar_graph(df, x, y, title):   
    fig = px.bar(df, x=x, y=y, title=title )
    fig.show()


def show_table(header_values, cell_values, title):
    
    # Create a Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(values=header_values,
                    fill_color='lightblue',
                    align='center'),
        cells=dict(values=cell_values,
                   fill_color='lavender',
                   align='center'))
    ])
    
    fig.update_layout(title=title)
    fig.show()

def show_dual_axis_chart(df, x, y1, y2, x_label, y1_label, y2_label, title):
    # Create figure
    fig = go.Figure()
    
    # Bar chart for batting average
    fig.add_trace(go.Bar(
        x=df[x],
        y=df[y1],
        name=y1_label,
        yaxis='y1',
        marker_color='skyblue'
    ))
    
    # Line chart for strike rate
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y2],
        name=y2_label,
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='firebrick', width=3)
    ))
    
    # Layout with dual Y axes
    fig.update_layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(
            title=y1_label,
            titlefont=dict(color='skyblue'),
            tickfont=dict(color='skyblue'),
            side='left'
        ),
        yaxis2=dict(
            title=y2_label,
            titlefont=dict(color='firebrick'),
            tickfont=dict(color='firebrick'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.5, y=1.1, orientation='h'),
        height=500
    )
    
    fig.show()

# %% [markdown]
# # Player Stats

# %% [markdown]
# ## Player Stats in a Season

# %%
# Player stats in a Season

player_name = "TM Head"
season = 2024

player_stats_in_season = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == player_name) & (ipl_ball_by_ball_stats['season_id'] == season)]

balls_faced, runs_scored, outs, fours, six, average, strike_rate = get_batter_stats(player_stats_in_season, player_name)

header_values = ["Player", "Runs Scored", "Balls Faced",  "Outs", "Fours", "Sixes", "Average", "Strike Rate"]
cell_values = [[player_name], [runs_scored], [balls_faced], [outs], [fours], [six], [average], [strike_rate]]
show_table(header_values=header_values, cell_values=cell_values, title=f"Performance Summary of {player_name} in Season {season}")

# %%
# Define the custom order
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

show_line_graph(df=player_stats_per_phase, x='over_phase', y='strike_rate', title='Strike rate per Phase')

# %%
show_player_strike_rate(player_stats_in_season, 'bowler_type', 'Strike Rate vs Bowler Type')

# %%
show_player_average(player_stats_in_season, 'bowler_type', player_name=player_name, title="Average vs Bowler Type")

# %%
player_stats_per_bowler = pd.merge(player_strike_rate_per_bowler, player_avg_per_bowler, on='bowler_type', how='inner')
player_stats_per_bowler['batter_runs'] = player_stats_per_bowler['batter_runs_x']

player_stats_per_bowler = player_stats_per_bowler.sort_values(by=['average', 'strike_rate'], ascending=[False, False])

show_dual_axis_chart(player_stats_per_bowler, x='bowler_type', y1='average', y2='strike_rate', x_label='Bowler Type',
                     y1_label='Batting Average', y2_label='Strike Rate', title='Performance vs Bowler Type')


# %% [markdown]
# ## Player Stats vs Particular Bowler Type

# %%
# players_data.head()
# players_data['bowl_style'].unique()

faster_bowlers = [
    'Left arm Medium fast',
    'Right arm Fast',
    'Right arm Medium',
    'Right arm Medium fast',
    'Left arm Fast medium',
    'Right arm Fast medium',
    'Left arm Medium',
    'Left arm Fast',
    'Right arm Fast Medium',
    'Right arm Bowler'  # assuming fast-medium default
]

spinners = [
    'Legbreak Googly',
    'Legbreak',
    'Right arm Offbreak',
    'Slow Left arm Orthodox',
    'Left arm Wrist spin',
    'Slow Left arm Orthodox, Left arm Wrist spin',
    'Right arm Offbreak, Legbreak Googly',
    'Right arm Medium, Legbreak',
    'Right arm Medium, Right arm Offbreak',
    'Right arm Offbreak, Legbreak',
    'Right arm Offbreak, Slow Left arm Orthodox',
    'Right arm Medium, Right arm Offbreak, Legbreak'
]

bowler_type = {
    'fast bowlers': faster_bowlers,
    'spin bowlers': spinners
}

# %%
player_name = "V Kohli"
bolwer_type_in_query = bowler_type['spin bowlers']

# bowler_type_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['Team'].isin(team_list)]
player_stats_vs_particular_bowler_type = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == player_name)]
# player_stats_vs_particular_bowler_type.head()
player_stats_vs_particular_bowler_type = player_stats_vs_particular_bowler_type[player_stats_vs_particular_bowler_type['bowler_type'].isin(bolwer_type_in_query)]

balls_faced, runs_scored, outs, fours, six, average, strike_rate = get_batter_stats(player_stats_vs_particular_bowler_type, player_name)

header_values = ["Player", "Runs Scored", "Balls Faced",  "Outs", "Fours", "Sixes", "Average", "Strike Rate"]
cell_values = [[player_name], [runs_scored], [balls_faced], [outs], [fours], [six], [average], [strike_rate]]
show_table(header_values=header_values, cell_values=cell_values, title=f"Performance Summary of {player_name} aginst Spinners")

# %%
show_player_strike_rate(player_stats_vs_particular_bowler_type, 'season_id', 'Strike Rate Per Season')

# %%
show_player_average(player_stats_vs_particular_bowler_type, 'season_id', player_name=player_name, title="Average Per Season Against Spinners")

# %%
player_name = "V Kohli"
bolwer_type_in_query = bowler_type['fast bowlers']

# bowler_type_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['Team'].isin(team_list)]
player_stats_vs_particular_bowler_type = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['batter'] == player_name)]
# player_stats_vs_particular_bowler_type.head()
player_stats_vs_particular_bowler_type = player_stats_vs_particular_bowler_type[player_stats_vs_particular_bowler_type['bowler_type'].isin(bolwer_type_in_query)]

balls_faced, runs_scored, outs, fours, six, average, strike_rate = get_batter_stats(player_stats_vs_particular_bowler_type, player_name)

header_values = ["Player", "Runs Scored", "Balls Faced",  "Outs", "Fours", "Sixes", "Average", "Strike Rate"]
cell_values = [[player_name], [runs_scored], [balls_faced], [outs], [fours], [six], [average], [strike_rate]]
show_table(header_values=header_values, cell_values=cell_values, title=f"Performance Summary of {player_name} against Fasters")

# %%
run_out_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['wicket_kind'] == 'run out']
player_involved_in_run_out = run_out_stats.groupby('player_out').size().reset_index()
player_involved_in_run_out.columns = ['player_out','instances']
# player_involved_in_run_out.colums = ['player_out', 'instances']
player_involved_in_run_out = player_involved_in_run_out.sort_values(by='instances', ascending=False)
player_involved_in_run_out.head(10)

# %%
run_out_stats_of_player_out_different_than_batter = ipl_ball_by_ball_stats[
    (ipl_ball_by_ball_stats['wicket_kind'] == 'run out') & 
    (ipl_ball_by_ball_stats['player_out'] != ipl_ball_by_ball_stats['batter'])
]

run_out_stats_of_player_out_different_than_batter
batter_stats = run_out_stats_of_player_out_different_than_batter.groupby('batter').size().reset_index()
batter_stats.columns = ['batter','instances']
# player_involved_in_run_out.colums = ['player_out', 'instances']
batter_stats = batter_stats.sort_values(by='instances', ascending=False)
batter_stats.head(10)



# %%

non_striker_stats = run_out_stats_of_player_out_different_than_batter.groupby('non_striker').size().reset_index()
non_striker_stats.columns = ['non_striker','instances']
# player_involved_in_run_out.colums = ['player_out', 'instances']
non_striker_stats = non_striker_stats.sort_values(by='instances', ascending=False)
non_striker_stats.head(10)

# %%
# Group and calculate total runs per season
runs_per_season = ipl_ball_by_ball_stats.groupby('season_id')['total_runs'].sum().reset_index()

fig = px.bar(runs_per_season, x='season_id', y='total_runs', title='Total Runs per Season')
fig.show()

# %%
legal_deliveries = ipl_ball_by_ball_stats[(ipl_ball_by_ball_stats['is_wide_ball'] == False) & (ipl_ball_by_ball_stats['is_no_ball'] == False)]

# Group by season and calculate runs per 100 balls
runs_per_100 = (
    legal_deliveries.groupby('season_id')['total_runs']
    .sum()
    .div(legal_deliveries.groupby('season_id').size())
    .mul(100)
)

# Convert to DataFrame for viewing
runs_per_100_df = runs_per_100.reset_index(name='strike_rate')
print(runs_per_100_df.head())

fig = px.line(runs_per_100_df, x='season_id', y='strike_rate', title='Strike rate per Season', markers=True )
fig.show()

# %%
print(ipl_ball_by_ball_stats['team_batting_name'].head())
print(type(ipl_ball_by_ball_stats['team_batting_name']))

# %%
# season_2024_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['season_id'] == 2024]
# # season_2024_stats.head()

# run_rate_per_over_in_2024_season = season_2024_stats.groupby('over_number')['total_runs'].sum().div(6).mul(100)
# runs_per_over_in_2024_season.head()

# # Group by season and calculate runs per 100 balls
# run_date_per_over_in_2024 = (
#     season_2024_stats.groupby(['over_number','team_batting_name'])['total_runs'].sum()
#     .div(season_2024_stats.groupby(['over_number','team_batting_name']).size())
#     .mul(6)
# )

# # Convert to DataFrame for viewing
# runs_rate_per_over_2024 = run_date_per_over_in_2024.reset_index(name='run_rate')
# runs_rate_per_over_2024.head()

# fig = px.line(runs_rate_per_over_2024, x='over_number', y='run_rate', color='team_batting_name', title='Run rate per Over in 2024 Season', markers=True )
# fig.show()


# Filter 2024 season
season_2024_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['season_id'] == 2024]

# Total runs per over and team
runs = season_2024_stats.groupby(['over_number', 'team_batting_name'])['total_runs'].sum()

# Total balls per over and team
balls = season_2024_stats.groupby(['over_number', 'team_batting_name']).size()

# Calculate run rate
run_rate = (runs / balls) * 6

# Reset index for plotting
run_rate_df = run_rate.reset_index(name='run_rate')
run_rate_df.head()


fig = px.line(run_rate_df, x='over_number', y='run_rate', color='team_batting_name', title='Run rate per Over in 2024 Season', markers=True )
fig.show()

# %%
virat_kohli_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['batter'] == 'V Kohli']

virat_kohli_stats = virat_kohli_stats.merge(matches_data[['match_id', 'city']], on='match_id', how='left')

virat_kohli_stats.head()

virat_kohli_stats_vs_mumbai = virat_kohli_stats[
    (virat_kohli_stats['city'] == 'Mumbai') & 
    (virat_kohli_stats['team_bowling'] == 3)
]

virat_kohli_stats_vs_mumbai.head()

vk_runs_per_season = virat_kohli_stats_vs_mumbai.groupby('season_id')['total_runs'].sum().reset_index()

fig = px.bar(vk_runs_per_season, x='season_id', y='total_runs', title='Virat Kohli at Wankhede over the years')
fig.show()

# %%
virat_kohli_stats = ipl_ball_by_ball_stats[ipl_ball_by_ball_stats['batter'] == 'V Kohli']

virat_kohli_stats = virat_kohli_stats.merge(matches_data[['match_id', 'city']], on='match_id', how='left')

virat_kohli_stats.head()

virat_kohli_stats_vs_csk = virat_kohli_stats[
    (virat_kohli_stats['city'] == 'Chennai') & 
    (virat_kohli_stats['team_bowling'] == 129)
]

virat_kohli_stats_vs_csk.head()

vk_runs_per_season = virat_kohli_stats_vs_csk.groupby('season_id')['total_runs'].sum().reset_index()

fig = px.bar(vk_runs_per_season, x='season_id', y='total_runs', title='Virat Kohli at Chepauk over the years')
fig.show()

# %%
#matches_and_team =  matches_data.merge(ipl_teams[['team_id', 'city']], on='match_id', how='left')

matches_and_team = matches_data.merge(
    ipl_teams[['team_id', 'team_name']],
    left_on='match_winner',
    right_on='team_id',
    how='left'
).rename(columns={'team_name': 'match_winner_team_name'}).drop(columns='team_id')

matches_and_team = matches_and_team[matches_and_team['season_id'] > 2019]
matches_and_team.head()



# %%
home_matches_per_team = matches_and_team['team1'].value_counts()
away_matches_per_team = matches_and_team['team2'].value_counts()

home_matches_per_team = matches_and_team['team1'].value_counts().reset_index()
home_matches_per_team.columns = ['team_id', 'total_matches']

away_matches_per_team = matches_and_team['team2'].value_counts().reset_index()
away_matches_per_team.columns = ['team_id', 'total_matches']



total_matches = pd.merge(home_matches_per_team, away_matches_per_team, on='team_id', how='inner')
total_matches['Total_Matches'] = total_matches['total_matches_x'] + total_matches['total_matches_y']
total_matches = total_matches.drop(columns=['total_matches_x', 'total_matches_y'])

total_wins = matches_and_team['match_winner'].value_counts().reset_index()
total_wins.columns = ['team_id', 'tota_wins']

teams_stats = pd.merge(total_wins, total_matches, on='team_id', how='inner')
teams_stats = teams_stats.merge(
    ipl_teams[['team_id', 'team_name']],
    left_on='team_id',
    right_on='team_id',
    how='left'
)
teams_stats['win_percentage'] = ( teams_stats['tota_wins'] / teams_stats['Total_Matches'] ) * 100
teams_stats


# %%
fig = px.bar(teams_stats, x='team_name', y='win_percentage', title='Win Percentage since 2020')
fig.show()

# %%



