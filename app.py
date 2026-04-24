import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px

# --- 1. DATA PREP ---
df = pd.read_csv('indian_space_startups.csv')

def clean_currency(value):
    if isinstance(value, str):
        return float(value.replace('$', '').replace('M', '').replace(',', '').strip())
    return value

df['Funding_Cleaned'] = df['Total Funding (Est.)'].apply(clean_currency)

# --- 2. THEME DEFINITIONS ---
THEMES = {
    'dark': {
        'background': '#0d1117',
        'card_bg': '#161b22',
        'text': '#e6edf3',
        'accent': '#58a6ff',
        'border': '#30363d',
        'plotly_template': 'plotly_dark'
    },
    'light': {
        'background': '#f0f2f5',
        'card_bg': '#ffffff',
        'text': '#1f2d3d',
        'accent': '#005cc5',
        'border': '#d1d5da',
        'plotly_template': 'plotly'
    }
}

# --- 3. INITIALIZE APP ---
app = dash.Dash(__name__)

# --- 4. LAYOUT ---
app.layout = html.Div(id='main-container', children=[
    
    # Custom Image Toggle & Header
    html.Div([
        html.Div([
            html.Span("Switch Theme ", style={'fontWeight': 'bold', 'verticalAlign': 'middle', 'marginRight': '10px'}),
            html.Img(
                id='theme-toggle-img',
                src=app.get_asset_url('toggle.png'),
                style={'width': '50px', 'cursor': 'pointer', 'verticalAlign': 'middle', 'transition': '0.3s'}
            ),
            dcc.Store(id='theme-state', data='dark')
        ], style={'textAlign': 'right', 'padding': '10px'}),

        html.H1("India NewSpace Market Intelligence", id='header-title',
                style={'textAlign': 'center', 'fontWeight': '800', 'marginTop': '0'}),
        html.P("Strategic Intelligence Dashboard | Q2 2026 Ecosystem Analysis", 
               id='header-subtitle', style={'textAlign': 'center', 'fontSize': '16px'}),
    ], style={'padding': '10px 20px'}),

    # Executive Summary Card
    html.Div([
        html.H3("Executive Summary", id='summary-title'),
        html.Ul([
            html.Li("The 'Consortium Shift': Transition from startup competition to national-scale infrastructure partnerships."),
            html.Li("Funding Density Gap: SSA and Ground Infrastructure remain high-value 'White Spaces' for new investment."),
            html.Li("Regional Expansion: Ahmedabad and Noida clusters emerging as strong hardware-focused competitors.")
        ], style={'lineHeight': '1.8', 'fontSize': '15px'})
    ], id='summary-card', style={'padding': '25px', 'borderRadius': '12px', 'marginBottom': '30px', 'transition': '0.3s'}),

    # Filter Dropdown (Spacing Corrected)
    html.Div([
        html.Label("Strategic Hub Filter:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='city-filter',
            options=[{'label': i, 'value': i} for i in sorted(df['HQ'].unique())],
            value=None,
            placeholder="Search City Hub...",
            style={'marginTop': '10px', 'color': '#000'}
        )
    ], style={'width': '35%', 'margin': '60px auto 50px auto', 'transition': '0.3s'}),

    # --- CHARTS GRID (With Borders & Separation) ---
    html.Div([
        # Row 1
        html.Div([
            html.Div([dcc.Graph(id='treemap-chart')], id='card-1', style={'borderRadius': '12px', 'padding': '15px'})
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px', 'boxSizing': 'border-box'}),
        
        html.Div([
            html.Div([dcc.Graph(id='bar-chart')], id='card-2', style={'borderRadius': '12px', 'padding': '15px'})
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '10px', 'boxSizing': 'border-box'}),
    ], style={'marginBottom': '25px'}),
    
    # Row 2
    html.Div([
        html.Div([
            html.Div([dcc.Graph(id='line-chart')], id='card-3', style={'borderRadius': '12px', 'padding': '15px'})
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '10px', 'boxSizing': 'border-box'}),
        
        html.Div([
            html.Div([dcc.Graph(id='bubble-chart')], id='card-4', style={'borderRadius': '12px', 'padding': '15px'})
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '10px', 'boxSizing': 'border-box'}),
    ])
])

# --- 5. CALLBACKS ---

@app.callback(
    Output('theme-state', 'data'),
    Input('theme-toggle-img', 'n_clicks'),
    State('theme-state', 'data'),
    prevent_initial_call=True
)
def toggle_theme_logic(n_clicks, current_theme):
    return 'light' if current_theme == 'dark' else 'dark'

@app.callback(
    [Output('main-container', 'style'),
     Output('header-title', 'style'),
     Output('summary-card', 'style'),
     Output('summary-title', 'style'),
     Output('theme-toggle-img', 'style'),
     Output('card-1', 'style'), # Added styling for cards
     Output('card-2', 'style'),
     Output('card-3', 'style'),
     Output('card-4', 'style'),
     Output('treemap-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('bubble-chart', 'figure')],
    [Input('city-filter', 'value'),
     Input('theme-state', 'data')]
)
def update_dashboard(selected_city, theme_mode):
    t = THEMES[theme_mode]
    
    # Base Styles
    main_style = {'backgroundColor': t['background'], 'color': t['text'], 'minHeight': '100vh', 'padding': '30px', 'transition': '0.3s'}
    header_style = {'textAlign': 'center', 'color': t['accent'], 'fontWeight': '800', 'transition': '0.3s'}
    
    # Shared Card Style (The Borders/Separation you requested)
    card_style = {
        'backgroundColor': t['card_bg'], 'padding': '15px', 'borderRadius': '12px', 
        'border': f"1px solid {t['border']}", 'boxShadow': '0 4px 12px 0 rgba(0,0,0,0.15)', 'transition': '0.3s'
    }
    
    summary_card_style = {**card_style, 'padding': '25px', 'marginBottom': '30px'}
    summary_title_style = {'color': t['accent'], 'borderBottom': f"1px solid {t['border']}", 'paddingBottom': '10px'}
    
    img_style = {
        'width': '50px', 'cursor': 'pointer', 'verticalAlign': 'middle', 'transition': '0.3s',
        'transform': 'rotate(180deg)' if theme_mode == 'light' else 'rotate(0deg)'
    }

    # Data Filter
    filtered_df = df if selected_city is None else df[df['HQ'] == selected_city]

    def apply_fig_theme(fig):
        fig.update_layout(
            template=t['plotly_template'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=t['text'],
            margin=dict(t=45, b=20, l=20, r=20)
        )
        return fig

    # Charts
    fig1 = apply_fig_theme(px.treemap(filtered_df, path=['Segment', 'Company'], values='Funding_Cleaned', color='Funding_Cleaned', color_continuous_scale='Blues', title="Market Concentration"))
    
    seg_data = filtered_df.groupby('Segment')['Funding_Cleaned'].sum().reset_index().sort_values('Funding_Cleaned', ascending=False)
    fig2 = apply_fig_theme(px.bar(seg_data, x='Segment', y='Funding_Cleaned', color='Funding_Cleaned', color_continuous_scale='Viridis', title="Funding by Segment"))
    
    growth = filtered_df.groupby('Year_Founded')['Company'].count().reset_index()
    fig3 = apply_fig_theme(px.line(growth, x='Year_Founded', y='Company', markers=True, title="Founding Velocity"))
    fig3.update_traces(line_color=t['accent'])
    
    matrix = filtered_df.groupby('Segment').agg(Count=('Company', 'count'), Total=('Funding_Cleaned', 'sum')).reset_index()
    matrix['Density'] = (matrix['Total'] / matrix['Count']).round(2)
    fig4 = apply_fig_theme(px.scatter(matrix, x='Count', y='Density', size='Total', color='Segment', hover_name='Segment', title="Market Opportunity Matrix"))

    return main_style, header_style, summary_card_style, summary_title_style, img_style, card_style, card_style, card_style, card_style, fig1, fig2, fig3, fig4

if __name__ == '__main__':
    app.run(debug=True)