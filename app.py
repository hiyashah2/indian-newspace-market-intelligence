import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# 1. DATA PREP
# ─────────────────────────────────────────────
df = pd.read_csv('data/indian_space_startups.csv')

def clean_currency(value):
    if isinstance(value, str):
        value = value.strip()
        if '₹' in value and 'Cr' in value:
            num = float(value.replace('₹', '').replace('Cr', '').replace(',', '').strip())
            return round(num * 0.012, 2)
        return float(value.replace('$', '').replace('M', '').replace(',', '').strip())
    return float(value) if value else 0.0

df['Funding_Cleaned'] = df['Total_Funding_USD_Est'].apply(clean_currency)

# ─────────────────────────────────────────────
# 2. PRE-COMPUTED ANALYTICS
# ─────────────────────────────────────────────
total_funding   = df['Funding_Cleaned'].sum()
total_companies = len(df)

lv_mask        = df['Segment'] == 'Launch Vehicles'
lv_funding_pct = round(df.loc[lv_mask, 'Funding_Cleaned'].sum() / total_funding * 100, 1)
lv_count_pct   = round(df[lv_mask].shape[0] / total_companies * 100, 1)

ssa_mask        = df['Segment'] == 'SSA'
ssa_funding_pct = round(df.loc[ssa_mask, 'Funding_Cleaned'].sum() / total_funding * 100, 1)
GLOBAL_SSA_PCT  = 9.0

post2020_pct = round(df[df['Year_Founded'] >= 2020].shape[0] / total_companies * 100, 1)

# ─────────────────────────────────────────────
# 3. BENCHMARK DATA & PROFILES
# ─────────────────────────────────────────────
GLOBAL_BENCHMARK = {
    'Launch Vehicles':   34.0,
    'Earth Observation': 18.0,
    'Satellite Systems': 14.0,
    'SSA':                9.0,
    'Communications':     8.0,
    'Propulsion':         6.0,
    'Data Analytics':     5.0,
    'Aerospace/Drones':   3.0,
    'Other':              3.0,
}

SEGMENT_MAP = {
    'Ground Stations':   'Other',
    'Navigation':        'Other',
    'Space Robotics':    'Other',
    'Spacecraft':        'Other',
    'Aerospace/Defence': 'Aerospace/Drones',
    'Aerospace/UAS':     'Aerospace/Drones',
}

def build_benchmark_df(source_df):
    mapped = source_df.copy()
    mapped['Segment_Mapped'] = mapped['Segment'].replace(SEGMENT_MAP)
    india_seg   = mapped.groupby('Segment_Mapped')['Funding_Cleaned'].sum().reset_index()
    india_total = india_seg['Funding_Cleaned'].sum()
    india_seg['India_Share'] = (india_seg['Funding_Cleaned'] / india_total * 100).round(1)
    india_seg = india_seg.rename(columns={'Segment_Mapped': 'Segment'})
    global_df = pd.DataFrame(list(GLOBAL_BENCHMARK.items()), columns=['Segment', 'Global_Share'])
    merged    = global_df.merge(india_seg[['Segment', 'India_Share']], on='Segment', how='left').fillna(0.0)
    melted = merged.melt(
        id_vars=['Segment'],
        value_vars=['Global_Share', 'India_Share'],
        var_name='Market', value_name='Share'
    )
    melted['Market'] = melted['Market'].map({
        'Global_Share': 'Global (BryceTech 2024)',
        'India_Share':  'India (This Dataset)'
    })
    return melted

PROFILES = [
    {
        "name": "Pixxel", "segment": "Earth Observation",
        "model": "Data-as-a-Service", "customer": "Agriculture, Mining, Govt, NASA",
        "description": "Operates India's first hyperspectral satellite constellation. Sells analytics platform access, not raw imagery.",
        "competitor": "Planet Labs (USA), Satellogic (Argentina)", "funding": "$95M Series B"
    },
    {
        "name": "SatSure", "segment": "Data Analytics",
        "model": "SaaS Platform", "customer": "Banks, Insurance firms, Agri Depts",
        "description": "Turns satellite data into crop loan risk scores for financial institutions. Pure analytics play.",
        "competitor": "Gro Intelligence (USA), Descartes Labs", "funding": "$29.5M Series A"
    },
    {
        "name": "Digantara", "segment": "SSA",
        "model": "Data-as-a-Service", "customer": "Satellite operators, Defence, US Space Command",
        "description": "Space debris tracking and orbital intelligence. India's only commercial SSA play at scale.",
        "competitor": "LeoLabs (USA), ExoAnalytic Solutions", "funding": "$64.5M Series B"
    },
    {
        "name": "Skyroot Aerospace", "segment": "Launch Vehicles",
        "model": "Launch-as-a-Service", "customer": "Small-sat operators, ISRO, Startups",
        "description": "Developed Vikram-S, India's first privately launched rocket. Targeting small-sat rideshare market.",
        "competitor": "Rocket Lab (NZ), Firefly Aerospace (USA)", "funding": "$99.8M Series B"
    },
    {
        "name": "Agnikul Cosmos", "segment": "Launch Vehicles",
        "model": "Launch-as-a-Service", "customer": "Small-sat operators, Research orgs",
        "description": "World's first single-piece 3D-printed rocket engine. Has its own private launchpad at Sriharikota.",
        "competitor": "ABL Space (USA), PLD Space (EU)", "funding": "$85.8M Pre-Series B"
    },
]

INSIGHT_CARDS_DATA = [
    {
        "num": "01",
        "headline": f"Launch Vehicles capture {lv_funding_pct}% of total funding.",
        "body": f"Despite being only {lv_count_pct}% of startups, launch attracts the highest capital intensity — signalling massive barriers to entry."
    },
    {
        "num": "02",
        "headline": f"SSA holds only {ssa_funding_pct}% of Indian NewSpace investment.",
        "body": f"Compared to {GLOBAL_SSA_PCT}% globally (BryceTech 2024), SSA is the most under-capitalised strategic gap in the ecosystem."
    },
    {
        "num": "03",
        "headline": f"{post2020_pct}% of active startups founded post-2020.",
        "body": "The 2020 space liberalisation reforms are the primary driver of current market velocity. Policy, not technology, triggered the founding surge."
    },
]

# ─────────────────────────────────────────────
# 4. THEMES
# ─────────────────────────────────────────────
THEMES = {
    'dark': {
        'background':      '#0d1117',
        'card_bg':         '#161b22',
        'text':            '#e6edf3',
        'accent':          '#58a6ff',
        'accent_muted':    'rgba(88,166,255,0.12)',
        'border':          '#30363d',
        'subtext':         '#8b949e',
        'plotly_template': 'plotly_dark',
        'bar_india':       '#58a6ff',
        'bar_global':      '#3fb950',
    },
    'light': {
        'background':      '#f0f2f5',
        'card_bg':         '#ffffff',
        'text':            '#1f2d3d',
        'accent':          '#005cc5',
        'accent_muted':    'rgba(0,92,197,0.10)',
        'border':          '#d1d5da',
        'subtext':         '#57606a',
        'plotly_template': 'plotly',
        'bar_india':       '#005cc5',
        'bar_global':      '#1a7f37',
    }
}

# ─────────────────────────────────────────────
# 5. APP INIT
# ─────────────────────────────────────────────
# meta_tags viewport is MANDATORY for mobile responsiveness.
# Without it, mobile browsers render at ~980px and ignore your CSS breakpoints.
app = dash.Dash(
    __name__,
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0"
    }]
)
server = app.server

# ─────────────────────────────────────────────
# 6. HELPER — insight cards
# ─────────────────────────────────────────────
def build_insight_cards(t):
    return [
        html.Div([
            html.Div(c["num"], style={
                'fontSize': '30px', 'fontWeight': '800',
                'color': t['accent'], 'opacity': '0.35', 'fontFamily': 'monospace'
            }),
            html.P(c["headline"], style={
                'fontSize': '14px', 'fontWeight': '700',
                'color': t['text'], 'margin': '5px 0'
            }),
            html.P(c["body"], style={
                'fontSize': '12px', 'color': t['subtext'],
                'lineHeight': '1.5', 'margin': '0'
            }),
        ],
        className='insight-card', # Hook for responsive.css
        style={
            'flex': '1', 'minWidth': '200px', 'padding': '15px',
            'borderLeft': f"3px solid {t['accent']}",
            'backgroundColor': t['accent_muted'],
            'borderRadius': '0 8px 8px 0',
        })
        for c in INSIGHT_CARDS_DATA
    ]

# ─────────────────────────────────────────────
# 7. LAYOUT
# ─────────────────────────────────────────────
app.layout = html.Div(id='main-container', children=[

    # ── Header ──────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Span("Switch Theme ", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            html.Img(
                id='theme-toggle-img',
                src=app.get_asset_url('toggle.png'),
                style={'width': '50px', 'cursor': 'pointer', 'transition': '0.3s'}
            ),
            dcc.Store(id='theme-state', data='dark'),
        ], style={'display': 'flex', 'alignItems': 'center',
                  'justifyContent': 'flex-end', 'padding': '10px'}),
        html.H1("India NewSpace Market Intelligence",
                id='header-title',
                style={'textAlign': 'center', 'fontWeight': '800', 'margin': '0'}),
        html.P("Strategic Intelligence Dashboard | Q2 2026 Ecosystem Analysis",
               id='header-subtitle',
               style={'textAlign': 'center', 'fontSize': '16px', 'marginTop': '6px'}),
    ], style={'padding': '10px 20px 0 20px'}),

    # ── Key Market Findings ──────────────────────────────────────────────────
    html.Div([
        html.H3("Key Market Findings", id='summary-title', style={'marginTop': '0'}),
        html.P(
            "Strategic analysis of capital flows and segment maturity across 40 Indian NewSpace companies.",
            id='summary-intro'
        ),
        # className='insight-row' → stacks vertically on mobile via CSS
        html.Div(id='insight-cards-row', className='insight-row'),
        html.Div([
            html.Div([
                html.Span(f"{total_companies}",
                          style={'fontSize': '22px', 'fontWeight': '700'}),
                html.Span(" companies tracked",
                          style={'fontSize': '13px', 'marginLeft': '6px'}),
            ], style={'display': 'inline-block', 'marginRight': '32px'}),
            html.Div([
                html.Span(f"${total_funding:.0f}M",
                          style={'fontSize': '22px', 'fontWeight': '700'}),
                html.Span(" total funding tracked",
                          style={'fontSize': '13px', 'marginLeft': '6px'}),
            ], style={'display': 'inline-block'}),
        ], id='stat-strip', style={'marginTop': '20px', 'paddingTop': '15px'}),
    ], id='summary-card',
       style={'padding': '25px', 'borderRadius': '12px', 'marginBottom': '24px'}),

    # ── City Filter ─────────────────────────────────────────────────────────
    # className='filter-container' → CSS makes this full-width on mobile
    html.Div([
        html.Label("Strategic Hub Filter:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='city-filter',
            options=[{'label': i, 'value': i} for i in sorted(df['HQ'].unique())],
            value=None,
            placeholder="Filter by city hub...",
            style={'marginTop': '8px', 'color': '#000'}
        )
    ], className='filter-container'),

    # ── Chart Row 1 ─────────────────────────────────────────────────────────
    # className='chart-row' → CSS switches to flex-direction:column on mobile
    html.Div([
        html.Div(
            dcc.Graph(id='treemap-chart',
                      config={'displayModeBar': False, 'responsive': True},
                      style={'height': '380px'}),
            id='card-1', className='chart-card'
        ),
        html.Div(
            dcc.Graph(id='bar-chart',
                      config={'displayModeBar': False, 'responsive': True},
                      style={'height': '380px'}),
            id='card-2', className='chart-card'
        ),
    ], className='chart-row'),

    # ── Chart Row 2 ─────────────────────────────────────────────────────────
    html.Div([
        html.Div(
            dcc.Graph(id='line-chart',
                      config={'displayModeBar': False, 'responsive': True},
                      style={'height': '380px'}),
            id='card-3', className='chart-card'
        ),
        html.Div(
            dcc.Graph(id='bubble-chart',
                      config={'displayModeBar': False, 'responsive': True},
                      style={'height': '380px'}),
            id='card-4', className='chart-card'
        ),
    ], className='chart-row'),

    # ── Chart 5: Benchmark — full width ─────────────────────────────────────
    html.Div([
        html.H4("India vs Global Gap Analysis",
                id='benchmark-label',
                style={'margin': '0 0 4px 0'}),
        html.P(
            "How India's investment mix compares to global private space funding (BryceTech 2024).",
            id='benchmark-sublabel',
            style={'fontSize': '12px', 'margin': '0 0 8px 0'}
        ),
        dcc.Graph(id='benchmark-chart',
                  config={'displayModeBar': False, 'responsive': True},
                  style={'height': '400px'}),
        html.P(
            "Source: BryceTech Start-Up Space 2024 (Global) | Custom Dataset (India)",
            id='benchmark-source',
            style={'fontSize': '11px', 'margin': '4px 0 0 0'}
        ),
    ], id='card-5',
       style={'padding': '20px', 'borderRadius': '12px', 'marginBottom': '20px'}),

    # ── Startup Intelligence Profiles ────────────────────────────────────────
    html.Div([
        html.H3("Startup Intelligence Profiles",
                id='profiles-title',
                style={'marginTop': '0', 'marginBottom': '16px'}),
        # className='profiles-scroll' → CSS gives touch scroll-snap on mobile
        html.Div(id='profiles-row', className='profiles-scroll'),
    ], id='profiles-section',
       style={'padding': '25px', 'borderRadius': '12px', 'marginBottom': '20px'}),

])

# ─────────────────────────────────────────────
# 8. CALLBACKS
# ─────────────────────────────────────────────

@app.callback(
    Output('theme-state', 'data'),
    Input('theme-toggle-img', 'n_clicks'),
    State('theme-state', 'data'),
    prevent_initial_call=True
)
def toggle_theme_logic(n, current):
    return 'light' if current == 'dark' else 'dark'


@app.callback(
    [
        Output('main-container',     'style'),
        Output('header-title',       'style'),
        Output('summary-card',       'style'),
        Output('summary-title',      'style'),
        Output('summary-intro',      'style'),
        Output('insight-cards-row',  'children'),
        Output('stat-strip',         'style'),
        Output('theme-toggle-img',   'style'),
        Output('card-1',             'style'),
        Output('card-2',             'style'),
        Output('card-3',             'style'),
        Output('card-4',             'style'),
        Output('card-5',             'style'),
        Output('benchmark-label',    'style'),
        Output('benchmark-sublabel', 'style'),
        Output('benchmark-source',   'style'),
        Output('profiles-title',     'style'),
        Output('profiles-section',   'style'),
        Output('profiles-row',       'children'),
        Output('treemap-chart',      'figure'),
        Output('bar-chart',          'figure'),
        Output('line-chart',         'figure'),
        Output('bubble-chart',       'figure'),
        Output('benchmark-chart',    'figure'),
    ],
    [Input('city-filter', 'value'),
     Input('theme-state', 'data')]
)
def update_dashboard(selected_city, theme_mode):
    t = THEMES[theme_mode]

    # ── Styles ──────────────────────────────────────────────────────────────
    main_style = {
        'backgroundColor': t['background'], 'color': t['text'],
        'minHeight': '100vh', 'padding': '30px', 'transition': '0.3s',
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    }

    # IMPORTANT: Width and flex behavior come from .chart-card in responsive.css.
    # Removed 'width' and 'flex' here to prevent overriding CSS media queries.
    chart_card_style = {
        'backgroundColor': t['card_bg'],
        'border':          f"1px solid {t['border']}",
        'borderRadius':    '12px',
        'overflow':        'hidden',
        'transition':      '0.3s',
    }
    summary_card_style = {
        'backgroundColor': t['card_bg'],
        'border':          f"1px solid {t['border']}",
        'borderRadius':    '12px',
        'padding':         '25px',
        'marginBottom':    '24px',
        'transition':      '0.3s',
    }
    full_card_style = {
        'backgroundColor': t['card_bg'],
        'border':          f"1px solid {t['border']}",
        'borderRadius':    '12px',
        'padding':         '20px',
        'marginBottom':    '20px',
        'transition':      '0.3s',
    }
    profiles_style = {
        'backgroundColor': t['card_bg'],
        'border':          f"1px solid {t['border']}",
        'borderRadius':    '12px',
        'padding':         '25px',
        'marginBottom':    '20px',
        'transition':      '0.3s',
    }
    stat_strip_style = {
        'marginTop':  '20px',
        'paddingTop': '15px',
        'borderTop':  f"1px solid {t['border']}",
    }
    img_style = {
        'width': '50px', 'cursor': 'pointer',
        'transform': 'rotate(180deg)' if theme_mode == 'light' else 'rotate(0deg)',
        'transition': '0.3s',
    }

    # ── Insight cards ───────────────────────────────────────────────────────
    insight_children = build_insight_cards(t)

    # ── Profile cards ───────────────────────────────────────────────────────
    profile_cards = [
        html.Div([
            html.Div(p['name'], style={
                'fontSize': '17px', 'fontWeight': '700', 'color': t['accent']
            }),
            html.Span(p['segment'], style={
                'fontSize': '10px', 'background': t['accent_muted'],
                'color': t['accent'], 'padding': '2px 8px', 'borderRadius': '8px',
                'display': 'inline-block', 'marginTop': '4px',
            }),
            html.P(p['description'], style={
                'fontSize': '12px', 'marginTop': '10px',
                'lineHeight': '1.5', 'color': t['text'],
            }),
            html.P(f"Model: {p['model']}",
                   style={'fontSize': '11px', 'color': t['subtext'], 'margin': '4px 0'}),
            html.P(f"Customers: {p['customer']}",
                   style={'fontSize': '11px', 'color': t['subtext'], 'margin': '4px 0'}),
            html.P(f"Global peer: {p['competitor']}",
                   style={'fontSize': '11px', 'color': t['subtext'], 'margin': '4px 0'}),
            html.P(p['funding'], style={
                'fontSize': '13px', 'fontWeight': '700',
                'color': '#3fb950', 'margin': '10px 0 0 0',
            }),
        ],
        className='profile-card',
        style={
            'padding':         '16px',
            'border':          f"1px solid {t['border']}",
            'backgroundColor': t['background'],
            'borderRadius':    '10px',
            'minWidth':        '230px',
            'maxWidth':        '260px',
            'flexShrink':      '0',
        })
        for p in PROFILES
    ]

    # ── Data filter (charts 1–4 only) ───────────────────────────────────────
    filtered_df = df if selected_city is None else df[df['HQ'] == selected_city]

    def apply_theme(fig):
        fig.update_layout(
            template=t['plotly_template'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=t['text'],
            font_size=12,
            margin=dict(t=50, b=40, l=20, r=20),
            legend=dict(font=dict(size=11)),
            autosize=True,
        )
        return fig

    # ── Fig 1: Treemap ───────────────────────────────────────────────────────
    fig1 = apply_theme(px.treemap(
        filtered_df,
        path=['Segment', 'Company'],
        values='Funding_Cleaned',
        title="Market Concentration by Funding",
        color='Funding_Cleaned',
        color_continuous_scale='Blues',
    ))
    fig1.update_traces(textfont_size=12)

    # ── Fig 2: Bar ──────────────────────────────────────────────────────────
    seg_data = (filtered_df
                .groupby('Segment')['Funding_Cleaned']
                .sum().reset_index()
                .sort_values('Funding_Cleaned', ascending=False))
    fig2 = apply_theme(px.bar(
        seg_data, x='Segment', y='Funding_Cleaned',
        title="Total Funding by Segment ($M)",
        color='Funding_Cleaned',
        color_continuous_scale='Viridis',
        labels={'Funding_Cleaned': 'Funding ($M)', 'Segment': ''},
    ))
    fig2.update_xaxes(tickangle=-35)

    # ── Fig 3: Line ─────────────────────────────────────────────────────────
    growth = (filtered_df
              .groupby('Year_Founded')['Company']
              .count().reset_index()
              .rename(columns={'Company': 'Startups_Founded'}))
    fig3 = apply_theme(px.line(
        growth, x='Year_Founded', y='Startups_Founded',
        title="Startup Founding Velocity",
        markers=True,
        labels={'Startups_Founded': 'Startups Founded', 'Year_Founded': 'Year'},
    ))
    fig3.update_traces(line_color=t['accent'], line_width=2.5, marker_size=7)
    fig3.add_vline(
        x=2020, line_dash='dash', line_color='#f78166',
        annotation_text=" 2020 Reforms",
        annotation_font_color='#f78166',
        annotation_position="top right",
    )

    # ── Fig 4: Bubble ───────────────────────────────────────────────────────
    matrix = (filtered_df
              .groupby('Segment')
              .agg(Count=('Company', 'count'), Total=('Funding_Cleaned', 'sum'))
              .reset_index())
    matrix['Avg_Funding'] = (matrix['Total'] / matrix['Count']).round(2)
    fig4 = apply_theme(px.scatter(
        matrix, x='Count', y='Avg_Funding',
        size='Total', color='Segment',
        hover_name='Segment',
        title="Market Opportunity Matrix",
        labels={'Count': 'No. of Startups', 'Avg_Funding': 'Avg Funding / Startup ($M)'},
        size_max=60,
    ))

    # ── Fig 5: Benchmark ─────────────────────────────────────────────────────
    melted_bm   = build_benchmark_df(df)
    global_data = melted_bm[melted_bm['Market'] == 'Global (BryceTech 2024)']
    india_data  = melted_bm[melted_bm['Market'] == 'India (This Dataset)']

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        name='Global (BryceTech 2024)',
        x=global_data['Segment'], y=global_data['Share'],
        marker_color=t['bar_global'],
    ))
    fig5.add_trace(go.Bar(
        name='India (This Dataset)',
        x=india_data['Segment'], y=india_data['Share'],
        marker_color=t['bar_india'],
    ))
    fig5.update_layout(
        barmode='group',
        yaxis_title='Share of Total Investment (%)',
        xaxis_title='',
        margin=dict(t=20, b=60, l=30, r=20),
        legend=dict(
            orientation='h',
            yanchor='bottom', y=1.02,
            xanchor='right',  x=1,
        ),
    )
    apply_theme(fig5)

    # ── Return ─────────────────────────────────────────────────────────────
    return (
        main_style,
        {'textAlign': 'center', 'color': t['accent'], 'fontWeight': '800', 'margin': '0'},
        summary_card_style,
        {'color': t['accent'], 'marginTop': '0'},
        {'color': t['subtext'], 'fontSize': '14px'},
        insight_children,
        stat_strip_style,
        img_style,
        chart_card_style,   # card-1
        chart_card_style,   # card-2
        chart_card_style,   # card-3
        chart_card_style,   # card-4
        full_card_style,    # card-5
        {'color': t['text'],    'margin': '0 0 4px 0', 'fontSize': '16px', 'fontWeight': '700'},
        {'color': t['subtext'], 'fontSize': '12px', 'margin': '0 0 8px 0'},
        {'color': t['subtext'], 'fontSize': '11px', 'margin': '4px 0 0 0'},
        {'color': t['accent'],  'marginTop': '0', 'marginBottom': '16px'},
        profiles_style,
        profile_cards,
        fig1, fig2, fig3, fig4, fig5,
    )


if __name__ == '__main__':
    app.run(debug=True)