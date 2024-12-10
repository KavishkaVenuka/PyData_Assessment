import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
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

# Group by World Cup year and calculate total runs
yearly_runs = crick_df.groupby('world_cup_year')['total_runs'].sum().reset_index()

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
])

# Callback to update the bar chart, pie chart, and line chart
@app.callback(
    [Output("matches-won-bar", "figure"),
     Output("match-category-pie", "figure"),
     Output("total-runs-line", "figure")],
    [Input("year-dropdown", "value")]
)
def update_graphs(selected_year):
    # Filter data by selected year
    filtered_df = crick_df[crick_df['world_cup_year'] == selected_year]

    if filtered_df.empty:
        empty_fig = go.Figure().update_layout(title="No Data Available")
        return empty_fig, empty_fig, empty_fig

    # Bar Chart: Matches Won by Each Team
    matches_won = filtered_df['winning_team'].value_counts().reset_index()
    matches_won.columns = ['winning_team', 'count']
    bar_fig = px.bar(matches_won, 
                     x='winning_team', 
                     y='count', 
                     labels={'winning_team': 'Team', 'count': 'Matches Won'},
                     title=f"Matches Won by Each Team in {selected_year}")

    # Pie Chart: Distribution of Match Categories
    match_categories = filtered_df['match_category'].value_counts().reset_index()
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

    return bar_fig, pie_fig, line_fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)