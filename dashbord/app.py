import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the processed dataset
crick_df = pd.read_csv("../data/out/processed_matches.csv")

# Ensure necessary columns are created or preprocessed


def extract_winning_team(result):
    if pd.isna(result) or not isinstance(result, str):
        return None
    if 'won by' in result.lower():
        return result.split('won')[0].strip()
    return None


# Add 'winning_team' column if not already present
if 'winning_team' not in crick_df.columns:
    crick_df['winning_team'] = crick_df['result'].apply(extract_winning_team)

# Calculate total runs
crick_df['total_runs'] = crick_df['team_1_runs'] + crick_df['team_2_runs']

# Extract runs for the top two batters


def extract_batter_runs(batter_info):
    try:
        # Extract the run value from the batter string (e.g., 'Player - 123 runs')
        runs = batter_info.split(' - ')[1].replace(' runs', '')
        return float(runs)
    except:
        return None  # Return None if extraction fails


# Apply the extraction function to the 'best_batters' column for both batters
crick_df['best_batter_1_runs'] = crick_df['best_batters'].str.split(
    ',').str[0].apply(extract_batter_runs)
crick_df['best_batter_2_runs'] = crick_df['best_batters'].str.split(
    ',').str[1].apply(extract_batter_runs)

# Group by World Cup year and calculate total runs
yearly_runs = crick_df.groupby('world_cup_year')[
    'total_runs'].sum().reset_index()

# Initialize Dash app
app = dash.Dash(__name__)

# App Layout
app.layout = html.Div([
    html.H1("ICC Cricket World Cup Dashboard", style={'textAlign': 'center'}),

    # Dropdown to filter by year
    html.Div([
        html.Label("Select World Cup Year:"),
        dcc.Dropdown(
            id="year-dropdown",
            options=[{"label": year, "value": year}
                     for year in sorted(crick_df['world_cup_year'].unique())],
            value=sorted(crick_df['world_cup_year'].unique())[0],
            clearable=False
        ),
    ], style={'width': '50%', 'margin': 'auto'}),

    # Bar Chart for Matches Won
    dcc.Graph(id="matches-won-bar"),

    # Pie Chart for Match Categories
    dcc.Graph(id="match-category-pie"),

    # Line Chart for Total Runs
    dcc.Graph(id="total-runs-line"),

    # Histogram for Runs Scored Distribution
    dcc.Graph(id="runs-distribution-histogram"),

    # Heatmap for Head-to-Head Team Performances
    dcc.Graph(id="head-to-head-heatmap"),
])

# Callback to update all 5 graphs


@app.callback(
    [Output("matches-won-bar", "figure"),
     Output("match-category-pie", "figure"),
     Output("total-runs-line", "figure"),
     Output("runs-distribution-histogram", "figure"),
     Output("head-to-head-heatmap", "figure")],
    [Input("year-dropdown", "value")]
)
def update_graphs(selected_year):
    # Filter data by selected year
    filtered_df = crick_df[crick_df['world_cup_year'] == selected_year]

    if filtered_df.empty:
        empty_fig = go.Figure().update_layout(title="No Data Available")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # Bar Chart: Matches Won by Each Team
    matches_won = filtered_df['winning_team'].value_counts().reset_index()
    matches_won.columns = ['winning_team', 'count']
    bar_fig = px.bar(matches_won,
                     x='winning_team',
                     y='count',
                     labels={'winning_team': 'Team', 'count': 'Matches Won'},
                     title=f"Matches Won by Each Team in {selected_year}")

    # Pie Chart: Distribution of Match Categories
    match_categories = filtered_df['match_category'].value_counts(
    ).reset_index()
    match_categories.columns = ['match_category', 'count']
    pie_fig = px.pie(match_categories,
                     values='count',
                     names='match_category',
                     title=f"Match Categories Distribution in {selected_year}")

    # Line Chart: Total Runs Scored Per Year (Across All Years)
    line_fig = px.line(yearly_runs,
                       x='world_cup_year',
                       y='total_runs',
                       markers=True,
                       title="Total Runs Scored Per Year",
                       labels={'world_cup_year': 'World Cup Year', 'total_runs': 'Total Runs'})

    # Histogram: Runs Scored Distribution (Team 1 vs Team 2)
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=filtered_df['team_1_runs'],
        name='Team 1 Runs',
        opacity=0.7,
        marker=dict(color='blue'),
        bingroup=1
    ))
    fig.add_trace(go.Histogram(
        x=filtered_df['team_2_runs'],
        name='Team 2 Runs',
        opacity=0.7,
        marker=dict(color='red'),
        bingroup=1
    ))

    fig.update_layout(
        barmode='overlay',
        title=f"Runs Distribution in {selected_year}",
        xaxis_title="Runs",
        yaxis_title="Frequency",
        template="plotly",
    )

    # Heatmap: Head-to-Head Team Performances
    head_to_head = filtered_df.groupby(['team_1', 'team_2'])[
        ['team_1_runs']].sum().reset_index()
    heatmap_data = head_to_head.pivot(
        index='team_1', columns='team_2', values='team_1_runs')
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        colorbar=dict(title="Runs Scored")
    ))
    heatmap_fig.update_layout(title=f"Head-to-Head Team Performances in {selected_year}",
                              xaxis_title="Opponent Team", yaxis_title="Team")

    return bar_fig, pie_fig, line_fig, fig, heatmap_fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)