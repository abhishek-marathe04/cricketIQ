import pandas as pd
from stats.common_functions.graph_functions import show_bar_graph, show_line_graph
from stats.common_functions.maths_utilities import add_strike_rate_to_df, get_average, get_legal_deliveries, get_number_of_fours, get_number_of_outs, get_number_of_six, get_strike_rate, get_wicket_stats


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
    
    return show_bar_graph(df=df_strike_rate, x=group_by_field, y='strike_rate', title=title)

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
    return show_bar_graph(df=df_avg, x=group_by_field, y='average', title=title)


def show_runs_per_season(df):
    df_per_season = (
        df
        .groupby(['season_id'])['batter_runs']
        .sum()
        .reset_index()
    )
    
    return show_line_graph(
        df=df_per_season,
        x='season_id',
        y='batter_runs',
        title='Runs Per Season',
    )
