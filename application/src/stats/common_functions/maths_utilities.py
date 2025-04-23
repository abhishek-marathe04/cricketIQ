

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