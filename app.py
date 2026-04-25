import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# 1. DATA PREP
# ─────────────────────────────────────────────
df = pd.read_csv('indian_space_startups.csv')

def clean_currency(value):
    """
    Handles: '$99.8M', '$1.2M', plain floats.
    New enriched CSV may also have '₹120 Cr' — convert using 1 Cr = $12,000 (83 INR/USD).
    """
    if isinstance(value, str):
        value = value.strip()
        if '₹' in value and 'Cr' in value:
            num = float(value.replace('₹', '').replace('Cr', '').replace(',', '').strip())
            return round(num * 0.012, 2)          # ₹ Cr → $M
        return float(value.replace('$', '').replace('M', '').replace(',', '').strip())
    return float(value) if value else 0.0

df['Funding_Cleaned'] = df['Total_Funding_USD_Est'].apply(clean_currency)


# ─────────────────────────────────────────────
# 2. PRE-COMPUTE INSIGHT CARD NUMBERS (whole-dataset level)
#    These are fixed analytics run once at startup.
#    Cards always show whole-ecosystem stats regardless of city filter,
#    so the headline figures stay meaningful even when a single city is selected.
# ─────────────────────────────────────────────

total_funding   = df['Funding_Cleaned'].sum()
total_companies = len(df)

# Card 1 — Launch vehicle capital concentration
lv_mask         = df['Segment'] == 'Launch Vehicles'
lv_funding_pct  = round(df.loc[lv_mask, 'Funding_Cleaned'].sum() / total_funding * 100, 1)
lv_count_pct    = round(df[lv_mask].shape[0] / total_companies * 100, 1)

# Card 2 — SSA white space vs global benchmark
ssa_mask        = df['Segment'] == 'SSA'
ssa_funding_pct = round(df.loc[ssa_mask, 'Funding_Cleaned'].sum() / total_funding * 100, 1)
# BryceTech Start-Up Space 2024 global SSA share benchmark
GLOBAL_SSA_PCT  = 9.0

# Card 3 — Post-2020 policy-reform founding surge
post2020_count  = df[df['Year_Founded'] >= 2020].shape[0]
post2020_pct    = round(post2020_count / total_companies * 100, 1)


# ─────────────────────────────────────────────
# 3. THEME DEFINITIONS
# ─────────────────────────────────────────────
THEMES = {
    'dark': {
        'background':       '#0d1117',
        'card_bg':          '#161b22',
        'text':             '#e6edf3',
        'accent':           '#58a6ff',
        'accent_muted':     'rgba(88,166,255,0.12)',
        'border':           '#30363d',
        'subtext':          '#8b949e',
        'plotly_template':  'plotly_dark',
        'insight_border':   '#58a6ff',
        'insight_num':      'rgba(88,166,255,0.18)',
    },
    'light': {
        'background':       '#f0f2f5',
        'card_bg':          '#ffffff',
        'text':             '#1f2d3d',
        'accent':           '#005cc5',
        'accent_muted':     'rgba(0,92,197,0.10)',
        'border':           '#d1d5da',
        'subtext':          '#57606a',
        'plotly_template':  'plotly',
        'insight_border':   '#005cc5',
        'insight_num':      'rgba(0,92,197,0.12)',
    }
}


# ─────────────────────────────────────────────
# 4. INSIGHT CARD DATA
#    Each card: number label, headline, body text, source note
# ─────────────────────────────────────────────
INSIGHT_CARDS = [
    {
        "num": "01",
        "headline": f"Launch Vehicles capture {lv_funding_pct}% of total funding — but only {lv_count_pct}% of startups.",
        "body": (
            f"With {df[lv_mask].shape[0]} companies absorbing ₹{lv_funding_pct}% of all private capital, "
            "the launch segment is the most capital-intensive in India's NewSpace ecosystem. "
            "This concentration signals high barriers to entry and limited room for new entrants "
            "without differentiated technology."
        ),
        "source": "Source: Dataset — Q2 2026"
    },
    {
        "num": "02",
        "headline": f"SSA holds only {ssa_funding_pct}% of Indian investment vs {GLOBAL_SSA_PCT}% globally — the clearest white space.",
        "body": (
            f"Space Situational Awareness companies (e.g. Digantara) account for just {ssa_funding_pct}% "
            f"of domestic private funding, against a {GLOBAL_SSA_PCT}% global benchmark (BryceTech 2024). "
            "As orbital congestion accelerates and defence demand grows, SSA represents the highest-opportunity "
            "underfunded segment for new capital and BD partnerships."
        ),
        "source": "Source: Dataset + BryceTech Start-Up Space 2024"
    },
    {
        "num": "03",
        "headline": f"{post2020_pct}% of active startups were founded after India's 2020 space reforms.",
        "body": (
            f"{post2020_count} of {total_companies} companies in this dataset were founded in 2020 or later — "
            "confirming the 2020 policy liberalisation (IN-SPACe creation, private launch access, FDI opening) "
            "as the primary growth catalyst. The ecosystem is structurally young, creating both high growth "
            "potential and execution risk across the value chain."
        ),
        "source": "Source: Dataset — founding year analysis"
    },
]


# ─────────────────────────────────────────────
# 5. INITIALIZE APP
# ─────────────────────────────────────────────
app = dash.Dash(__name__)
server = app.server   # Required by Render


# ─────────────────────────────────────────────
# 6. HELPER — build insight cards HTML (theme-aware)
# ─────────────────────────────────────────────
def build_insight_cards(t):
    cards = []
    for card in INSIGHT_CARDS:
        cards.append(
            html.Div([
                # Large number label
                html.Div(
                    card["num"],
                    style={
                        'fontSize':     '36px',
                        'fontWeight':   '800',
                        'color':        t['accent'],
                        'opacity':      '0.35',
                        'lineHeight':   '1',
                        'marginBottom': '8px',
                        'fontFamily':   'monospace',
                    }
                ),
                # Headline
                html.P(
                    card["headline"],
                    style={
                        'fontSize':     '14px',
                        'fontWeight':   '600',
                        'color':        t['text'],
                        'margin':       '0 0 8px 0',
                        'lineHeight':   '1.5',
                    }
                ),
                # Body
                html.P(
                    card["body"],
                    style={
                        'fontSize':   '13px',
                        'color':      t['subtext'],
                        'margin':     '0 0 10px 0',
                        'lineHeight': '1.6',
                    }
                ),
                # Source note
                html.Span(
                    card["source"],
                    style={
                        'fontSize':      '11px',
                        'color':         t['subtext'],
                        'opacity':       '0.7',
                        'fontStyle':     'italic',
                    }
                ),
            ], style={
                'flex':           '1',
                'minWidth':       '240px',
                'padding':        '20px 22px',
                'borderLeft':     f"3px solid {t['insight_border']}",
                'background':     t['accent_muted'],
                'borderRadius':   '0 10px 10px 0',
            })
        )
    return cards


# ─────────────────────────────────────────────
# 7. LAYOUT
# ─────────────────────────────────────────────
app.layout = html.Div(id='main-container', children=[

    # ── Header ──────────────────────────────
    html.Div([
        html.Div([
            html.Span(
                "Switch Theme ",
                style={'fontWeight': 'bold', 'verticalAlign': 'middle', 'marginRight': '10px'}
            ),
            html.Img(
                id='theme-toggle-img',
                src=app.get_asset_url('toggle.png'),
                style={'width': '50px', 'cursor': 'pointer', 'verticalAlign': 'middle', 'transition': '0.3s'}
            ),
            dcc.Store(id='theme-state', data='dark')
        ], style={'textAlign': 'right', 'padding': '10px'}),

        html.H1(
            "India NewSpace Market Intelligence",
            id='header-title',
            style={'textAlign': 'center', 'fontWeight': '800', 'marginTop': '0'}
        ),
        html.P(
            "Strategic Intelligence Dashboard | Q2 2026 Ecosystem Analysis",
            id='header-subtitle',
            style={'textAlign': 'center', 'fontSize': '16px'}
        ),
    ], style={'padding': '10px 20px'}),

    # ── Executive Summary Card ───────────────
    html.Div([
        html.H3("Key Market Findings", id='summary-title'),
        html.P(
            "India's NewSpace ecosystem spans 40+ funded companies across 9 segments. "
            "Three structural patterns define where capital flows, where gaps exist, "
            "and what the 2020 policy reforms actually changed.",
            id='summary-intro',
            style={'fontSize': '14px', 'marginBottom': '20px', 'lineHeight': '1.6'}
        ),

        # ── Three insight cards in a flex row ──
        html.Div(
            id='insight-cards-row',
            children=[],          # populated by callback
            style={
                'display':   'flex',
                'gap':       '16px',
                'flexWrap':  'wrap',
            }
        ),

        # ── Dataset stat strip ──────────────────
        html.Div([
            html.Div([
                html.Span(
                    f"{total_companies}",
                    style={'fontSize': '22px', 'fontWeight': '700'}
                ),
                html.Span(
                    " companies tracked",
                    style={'fontSize': '13px', 'marginLeft': '4px'}
                ),
            ], style={'marginRight': '30px', 'display': 'inline-block'}),

            html.Div([
                html.Span(
                    f"${total_funding:.0f}M",
                    style={'fontSize': '22px', 'fontWeight': '700'}
                ),
                html.Span(
                    " total private funding",
                    style={'fontSize': '13px', 'marginLeft': '4px'}
                ),
            ], style={'marginRight': '30px', 'display': 'inline-block'}),

            html.Div([
                html.Span(
                    "2007–2026",
                    style={'fontSize': '22px', 'fontWeight': '700'}
                ),
                html.Span(
                    " founding span",
                    style={'fontSize': '13px', 'marginLeft': '4px'}
                ),
            ], style={'display': 'inline-block'}),

        ], id='stat-strip', style={
            'marginTop':    '24px',
            'paddingTop':   '16px',
            'borderTop':    '1px solid',   # color set by callback
        }),

    ], id='summary-card', style={
        'padding':       '25px',
        'borderRadius':  '12px',
        'marginBottom':  '30px',
        'transition':    '0.3s'
    }),

    # ── City Filter ─────────────────────────
    html.Div([
        html.Label("Strategic Hub Filter:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='city-filter',
            options=[{'label': i, 'value': i} for i in sorted(df['HQ'].unique())],
            value=None,
            placeholder="Search City Hub...",
            style={'marginTop': '10px', 'color': '#000'}
        )
    ], style={'width': '35%', 'margin': '40px auto 40px auto', 'transition': '0.3s'}),

    # ── Charts Grid ─────────────────────────
    html.Div([
        # Row 1
        html.Div([
            html.Div([dcc.Graph(id='treemap-chart')],
                     id='card-1', style={'borderRadius': '12px', 'padding': '15px'}),
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top',
                  'paddingRight': '10px', 'boxSizing': 'border-box'}),

        html.Div([
            html.Div([dcc.Graph(id='bar-chart')],
                     id='card-2', style={'borderRadius': '12px', 'padding': '15px'}),
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top',
                  'paddingLeft': '10px', 'boxSizing': 'border-box'}),
    ], style={'marginBottom': '25px'}),

    # Row 2
    html.Div([
        html.Div([
            html.Div([dcc.Graph(id='line-chart')],
                     id='card-3', style={'borderRadius': '12px', 'padding': '15px'}),
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top',
                  'paddingRight': '10px', 'boxSizing': 'border-box'}),

        html.Div([
            html.Div([dcc.Graph(id='bubble-chart')],
                     id='card-4', style={'borderRadius': '12px', 'padding': '15px'}),
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top',
                  'paddingLeft': '10px', 'boxSizing': 'border-box'}),
    ]),

])


# ─────────────────────────────────────────────
# 8. CALLBACKS
# ─────────────────────────────────────────────

# ── 8a. Theme toggle ──────────────────────────
@app.callback(
    Output('theme-state', 'data'),
    Input('theme-toggle-img', 'n_clicks'),
    State('theme-state', 'data'),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    return 'light' if current_theme == 'dark' else 'dark'


# ── 8b. Main dashboard update ─────────────────
@app.callback(
    [
        Output('main-container',    'style'),
        Output('header-title',      'style'),
        Output('summary-card',      'style'),
        Output('summary-title',     'style'),
        Output('summary-intro',     'style'),
        Output('insight-cards-row', 'children'),
        Output('stat-strip',        'style'),
        Output('theme-toggle-img',  'style'),
        Output('card-1',            'style'),
        Output('card-2',            'style'),
        Output('card-3',            'style'),
        Output('card-4',            'style'),
        Output('treemap-chart',     'figure'),
        Output('bar-chart',         'figure'),
        Output('line-chart',        'figure'),
        Output('bubble-chart',      'figure'),
    ],
    [
        Input('city-filter',  'value'),
        Input('theme-state',  'data'),
    ]
)
def update_dashboard(selected_city, theme_mode):
    t = THEMES[theme_mode]

    # ── Shared styles ───────────────────────────
    main_style = {
        'backgroundColor': t['background'],
        'color':           t['text'],
        'minHeight':       '100vh',
        'padding':         '30px',
        'transition':      '0.3s',
    }
    header_style = {
        'textAlign':  'center',
        'color':      t['accent'],
        'fontWeight': '800',
        'transition': '0.3s',
    }
    card_style = {
        'backgroundColor': t['card_bg'],
        'padding':         '15px',
        'borderRadius':    '12px',
        'border':          f"1px solid {t['border']}",
        'boxShadow':       '0 4px 12px 0 rgba(0,0,0,0.15)',
        'transition':      '0.3s',
    }
    summary_card_style = {
        **card_style,
        'padding':      '25px',
        'marginBottom': '30px',
    }
    summary_title_style = {
        'color':         t['accent'],
        'borderBottom':  f"1px solid {t['border']}",
        'paddingBottom': '10px',
    }
    summary_intro_style = {
        'fontSize':     '14px',
        'color':        t['subtext'],
        'marginBottom': '20px',
        'lineHeight':   '1.6',
    }
    stat_strip_style = {
        'marginTop':  '24px',
        'paddingTop': '16px',
        'borderTop':  f"1px solid {t['border']}",
        'color':      t['text'],
    }
    img_style = {
        'width':     '50px',
        'cursor':    'pointer',
        'verticalAlign': 'middle',
        'transition': '0.3s',
        'transform': 'rotate(180deg)' if theme_mode == 'light' else 'rotate(0deg)',
    }

    # ── Build insight cards with current theme ──
    insight_children = build_insight_cards(t)

    # ── Data filter (charts only) ───────────────
    filtered_df = df if selected_city is None else df[df['HQ'] == selected_city]

    def apply_fig_theme(fig):
        fig.update_layout(
            template=t['plotly_template'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=t['text'],
            margin=dict(t=45, b=20, l=20, r=20),
        )
        return fig

    # ── Chart 1 — Treemap ───────────────────────
    fig1 = apply_fig_theme(
        px.treemap(
            filtered_df,
            path=['Segment', 'Company'],
            values='Funding_Cleaned',
            color='Funding_Cleaned',
            color_continuous_scale='Blues',
            title="Market Concentration by Segment & Company",
        )
    )

    # ── Chart 2 — Funding bar ───────────────────
    seg_data = (
        filtered_df
        .groupby('Segment')['Funding_Cleaned']
        .sum()
        .reset_index()
        .sort_values('Funding_Cleaned', ascending=False)
    )
    fig2 = apply_fig_theme(
        px.bar(
            seg_data,
            x='Segment',
            y='Funding_Cleaned',
            color='Funding_Cleaned',
            color_continuous_scale='Viridis',
            title="Total Private Funding by Segment ($M)",
            labels={'Funding_Cleaned': 'Funding ($M)', 'Segment': ''},
        )
    )
    fig2.update_layout(xaxis_tickangle=-30)

    # ── Chart 3 — Founding velocity ─────────────
    growth = (
        filtered_df
        .groupby('Year_Founded')['Company']
        .count()
        .reset_index()
        .rename(columns={'Company': 'Startups_Founded'})
    )
    fig3 = apply_fig_theme(
        px.line(
            growth,
            x='Year_Founded',
            y='Startups_Founded',
            markers=True,
            title="Startup Founding Velocity (Policy Reform Impact)",
            labels={'Year_Founded': 'Year', 'Startups_Founded': 'Startups Founded'},
        )
    )
    fig3.update_traces(line_color=t['accent'], marker_color=t['accent'])
    # Annotate 2020 reform year
    fig3.add_vline(
        x=2020,
        line_dash='dash',
        line_color='#f78166',
        annotation_text="2020 Reforms",
        annotation_position="top right",
        annotation_font_color='#f78166',
    )

    # ── Chart 4 — Market opportunity matrix ─────
    matrix = (
        filtered_df
        .groupby('Segment')
        .agg(Count=('Company', 'count'), Total=('Funding_Cleaned', 'sum'))
        .reset_index()
    )
    matrix['Avg_Funding_Per_Co'] = (matrix['Total'] / matrix['Count']).round(2)
    fig4 = apply_fig_theme(
        px.scatter(
            matrix,
            x='Count',
            y='Avg_Funding_Per_Co',
            size='Total',
            color='Segment',
            hover_name='Segment',
            title="Market Opportunity Matrix — Density vs Capital per Company",
            labels={
                'Count':               'Number of Startups',
                'Avg_Funding_Per_Co':  'Avg Funding per Company ($M)',
                'Total':               'Total Segment Funding ($M)',
            },
        )
    )

    return (
        main_style,
        header_style,
        summary_card_style,
        summary_title_style,
        summary_intro_style,
        insight_children,
        stat_strip_style,
        img_style,
        card_style,
        card_style,
        card_style,
        card_style,
        fig1,
        fig2,
        fig3,
        fig4,
    )


# ─────────────────────────────────────────────
# 9. RUN
# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)