

import pandas as pd
import plotly.express as px


def run_rate_per_phase(df, query_field, title):
    runs = df.groupby(['over_phase', query_field])['total_runs'].sum()

    # Total balls per over and team
    balls = df.groupby(['over_phase', query_field]).size()
    
    # Calculate run rate
    run_rate = (runs / balls) * 6
    
    # Reset index for plotting
    run_rate_df = run_rate.reset_index(name='run_rate')
    
    # Define desired order
    phase_order = ['Powerplay', 'Middle Overs', 'Death Overs']
    
    # Set 'over_phase' as a categorical column with this order
    run_rate_df['over_phase'] = pd.Categorical(run_rate_df['over_phase'], categories=phase_order, ordered=True)
    
    
    fig = px.line(
        run_rate_df,
        x='over_phase',
        y='run_rate',
        color=query_field,
        title=title,
        markers=True
    )
    fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':phase_order})
    return fig