
import plotly.graph_objects as go
import plotly.express as px
# Common Graph functions

def show_line_graph(df, x, y, title):   
    fig = px.line(df, x=x, y=y, title=title, markers=True )
    # fig.show()
    return fig


def show_bar_graph(df, x, y, title):   
    fig = px.bar(df, x=x, y=y, title=title )
    # fig.show()
    return fig


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
    
    fig.update_layout(title=title, 
                      height=270,  # Reduce height of table
                      font_size=10)  # Smaller font size)
    # fig.show()
    return fig

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
    
    # fig.show()
    return fig