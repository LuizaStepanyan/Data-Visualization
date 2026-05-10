import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_jordan_data, get_kpis

dash.register_page(__name__, path="/", name="Pricing Overview")

# Shared style tokens
CARD_STYLE = {
    "background": "#0F2040",
    "border": "1px solid #1A3060",
    "borderRadius": "12px",
    "padding": "1.25rem",
}
TITLE_STYLE = {
    "fontFamily": "'Syne', sans-serif",
    "fontWeight": "700",
    "color": "#E8F0FF",
    "fontSize": "0.85rem",
    "letterSpacing": "0.05em",
    "textTransform": "uppercase",
    "marginBottom": "1rem",
}
PLOT_BG = "#0F2040"
PAPER_BG = "#0F2040"
FONT_COLOR = "#C5D0E8"
GRID_COLOR = "#1A3060"
ACCENT = "#4D7EF7"
USA_COLOR = "#FF6B4D"

def kpi_card(label, value_id, icon, accent="#4D7EF7"):
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "1.4rem"}),
            html.Div([
                html.Div(id=value_id, style={
                    "fontFamily": "'Syne', sans-serif", "fontWeight": "800",
                    "color": "#F0F4FF", "fontSize": "1.5rem", "lineHeight": "1"
                }),
                html.Div(label, style={
                    "color": "#7A90B8", "fontSize": "0.7rem",
                    "textTransform": "uppercase", "letterSpacing": "0.08em", "marginTop": "3px"
                })
            ])
        ], style={"display": "flex", "gap": "0.75rem", "alignItems": "center"}),
        html.Div(style={
            "position": "absolute", "bottom": 0, "left": 0,
            "height": "3px", "width": "100%",
            "background": f"linear-gradient(90deg, {accent}, transparent)",
            "borderRadius": "0 0 12px 12px"
        })
    ], style={**CARD_STYLE, "position": "relative", "overflow": "hidden"})

layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.P("JORDAN CARS MARKET 2026", style={
                "color": ACCENT, "fontSize": "0.7rem", "fontWeight": "700",
                "letterSpacing": "0.15em", "margin": "0", "fontFamily": "'Syne', sans-serif"
            }),
            html.H1("Pricing Overview", style={
                "fontFamily": "'Syne', sans-serif", "fontWeight": "800",
                "color": "#F0F4FF", "margin": "0.25rem 0 0.5rem",
                "fontSize": "2rem", "letterSpacing": "-0.03em"
            }),
            html.P("Explore price distributions, trends by year, and Jordan vs USA comparison",
                   style={"color": "#7A90B8", "margin": 0, "fontSize": "0.85rem"})
        ])
    ], style={"padding": "2rem 2rem 1.5rem"}),

    # Filter bar
    html.Div([
        html.Div([
            html.Label("Year Range", style={"color": "#7A90B8", "fontSize": "0.7rem",
                                            "textTransform": "uppercase", "letterSpacing": "0.08em",
                                            "display": "block", "marginBottom": "6px"}),
            dcc.RangeSlider(
                id="p1-year-slider", min=1995, max=2026, step=1,
                value=[2005, 2026],
                marks={y: {"label": str(y), "style": {"color": "#7A90B8", "fontSize": "0.65rem"}}
                       for y in range(1995, 2027, 5)},
                tooltip={"placement": "bottom", "always_visible": False}
            )
        ], style={"flex": "1", "minWidth": "280px"}),

        html.Div([
            html.Label("Condition", style={"color": "#7A90B8", "fontSize": "0.7rem",
                                           "textTransform": "uppercase", "letterSpacing": "0.08em",
                                           "display": "block", "marginBottom": "6px"}),
            dcc.Dropdown(
                id="p1-condition-dd",
                options=[{"label": "All", "value": "All"},
                         {"label": "Used", "value": "used"},
                         {"label": "New (Zero)", "value": "New (Zero)"}],
                value="All", clearable=False,
                style={"background": "#0A1628", "color": "#C5D0E8", "border": "1px solid #1A3060",
                       "fontSize": "0.82rem"}
            )
        ], style={"width": "160px"}),

        html.Div([
            html.Label("Price Scale", style={"color": "#7A90B8", "fontSize": "0.7rem",
                                              "textTransform": "uppercase", "letterSpacing": "0.08em",
                                              "display": "block", "marginBottom": "6px"}),
            dcc.Dropdown(
                id="p1-scale-dd",
                options=[{"label": "Linear", "value": "linear"},
                         {"label": "Log", "value": "log"}],
                value="linear", clearable=False,
                style={"background": "#0A1628", "color": "#C5D0E8", "border": "1px solid #1A3060",
                       "fontSize": "0.82rem"}
            )
        ], style={"width": "130px"}),
    ], style={
        "display": "flex", "gap": "1.5rem", "flexWrap": "wrap",
        "alignItems": "flex-end", "padding": "0 2rem 1.5rem",
        "background": "#0D1B2E"
    }),

    # KPI cards row
    html.Div([
        kpi_card("Total Listings", "kpi-listings", "📋"),
        kpi_card("Median Price", "kpi-median", "💰", "#00D4AA"),
        kpi_card("Mean Price", "kpi-mean", "📊", "#F7C84D"),
        kpi_card("Median Mileage", "kpi-mileage", "🛣️", "#FF6B4D"),
        kpi_card("Top Brand", "kpi-brand", "🏆", "#B44DFF"),
    ], style={
        "display": "grid",
        "gridTemplateColumns": "repeat(5, 1fr)",
        "gap": "1rem",
        "padding": "0 2rem 1.5rem"
    }),

    # Row 1: Price distribution + Median by year
    html.Div([
        html.Div([
            html.Div("Price Distribution: Jordan vs USA", style=TITLE_STYLE),
            dcc.Graph(id="p1-hist", config={"displayModeBar": False},
                      style={"height": "300px"})
        ], style={**CARD_STYLE, "flex": "1"}),

        html.Div([
            html.Div("Median Price by Model Year", style=TITLE_STYLE),
            dcc.Graph(id="p1-year-line", config={"displayModeBar": False},
                      style={"height": "300px"})
        ], style={**CARD_STYLE, "flex": "1"}),
    ], style={"display": "flex", "gap": "1rem", "padding": "0 2rem 1rem"}),

    # Row 2: Boxplot mileage vs price + scatter
    html.Div([
        html.Div([
            html.Div("Price vs Mileage by Fuel Type", style=TITLE_STYLE),
            dcc.Graph(id="p1-scatter", config={"displayModeBar": False},
                      style={"height": "320px"})
        ], style={**CARD_STYLE, "flex": "3"}),

        html.Div([
            html.Div([
                html.Span("Stat", style={"color": "#7A90B8", "fontSize": "0.7rem",
                                          "textTransform": "uppercase", "letterSpacing": "0.08em"}),
                html.Span(" Toggle", style={"color": ACCENT, "fontSize": "0.7rem",
                                             "textTransform": "uppercase", "letterSpacing": "0.08em"}),
            ], style={"marginBottom": "1rem"}),
            dcc.RadioItems(
                id="p1-stat-toggle",
                options=[{"label": " Median", "value": "median"},
                         {"label": " Mean", "value": "mean"}],
                value="median",
                labelStyle={"display": "flex", "alignItems": "center", "gap": "6px",
                            "color": "#C5D0E8", "fontSize": "0.82rem", "marginBottom": "8px"},
                inputStyle={"accentColor": ACCENT}
            ),
            html.Hr(style={"borderColor": "#1A3060", "margin": "1rem 0"}),
            html.Div("Price Percentiles (Jordan)", style={
                "color": "#7A90B8", "fontSize": "0.7rem",
                "textTransform": "uppercase", "letterSpacing": "0.08em", "marginBottom": "0.75rem"
            }),
            html.Div(id="p1-percentiles"),
        ], style={**CARD_STYLE, "flex": "1"}),
    ], style={"display": "flex", "gap": "1rem", "padding": "0 2rem 2rem"}),

], style={"background": "#0D1B2E", "minHeight": "100vh"})


def _apply_filters(df, year_range, condition):
    mask = (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])
    if condition != "All":
        mask &= df["Condition"] == condition
    return df[mask]


@callback(
    Output("kpi-listings", "children"),
    Output("kpi-median", "children"),
    Output("kpi-mean", "children"),
    Output("kpi-mileage", "children"),
    Output("kpi-brand", "children"),
    Output("p1-hist", "figure"),
    Output("p1-year-line", "figure"),
    Output("p1-scatter", "figure"),
    Output("p1-percentiles", "children"),
    Input("p1-year-slider", "value"),
    Input("p1-condition-dd", "value"),
    Input("p1-scale-dd", "value"),
    Input("p1-stat-toggle", "value"),
)
def update_page1(year_range, condition, scale, stat):
    df = load_jordan_data()
    df = _apply_filters(df, year_range, condition)

    kpis = get_kpis(df)

    # KPI text
    listings_txt = f"{kpis['total_listings']:,}"
    median_txt   = f"${kpis['median_price_usd']:,.0f}"
    mean_txt     = f"${kpis['mean_price_usd']:,.0f}"
    mileage_txt  = f"{kpis['median_mileage']:,.0f} km"
    brand_txt    = kpis["top_brand"]

    layout_base = dict(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR, family="DM Sans, sans-serif", size=11),
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0, font=dict(size=10)),
    )

    #Histogram 
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=df["Price_USD"], nbinsx=50, name="Jordan",
        opacity=0.75, marker_color=ACCENT, histnorm="percent"
    ))
    jordan_median = df["Price_USD"].median()
    jordan_mean   = df["Price_USD"].mean()
    fig_hist.add_vline(x=jordan_median, line_dash="dash", line_color=ACCENT, line_width=1.5,
                       annotation_text=f"Median ${jordan_median:,.0f}",
                       annotation_font_color=ACCENT, annotation_font_size=10)
    fig_hist.add_vline(x=jordan_mean, line_dash="dot", line_color="#F7C84D", line_width=1.5,
                       annotation_text=f"Mean ${jordan_mean:,.0f}",
                       annotation_font_color="#F7C84D", annotation_font_size=10)
    fig_hist.update_layout(
        **layout_base,
        xaxis_type=scale,
        xaxis_title="Price (USD)", yaxis_title="% Listings",
        bargap=0.05,
    )

    # Year line 
    agg_fn = "median" if stat == "median" else "mean"
    by_year = df.groupby("Year")["Price_USD"].agg(agg_fn).reset_index()
    fig_year = go.Figure()
    fig_year.add_trace(go.Scatter(
        x=by_year["Year"], y=by_year["Price_USD"],
        mode="lines+markers", name="Jordan",
        line=dict(color=ACCENT, width=2.5),
        marker=dict(size=5, color=ACCENT),
        fill="tozeroy", fillcolor="rgba(77,126,247,0.08)"
    ))
    fig_year.update_layout(
        **layout_base,
        yaxis_type=scale,
        xaxis_title="Model Year", yaxis_title=f"{stat.title()} Price (USD)"
    )

    # Scatter mileage vs price 
    fuel_colors = {
        "Gasoline": "#636EFA", "Diesel": "#EF553B",
        "Hybrid": "#00CC96", "Electric": "#AB63FA", "Other": "#FFA15A"
    }
    df_sample = df.sample(min(len(df), 600), random_state=42)
    fig_scatter = go.Figure()
    for fuel, color in fuel_colors.items():
        sub = df_sample[df_sample["Fuel_Type"] == fuel]
        if sub.empty:
            continue
        fig_scatter.add_trace(go.Scatter(
            x=sub["Mileage_Avg"], y=sub["Price_USD"],
            mode="markers", name=fuel,
            marker=dict(color=color, size=5, opacity=0.65,
                        line=dict(width=0.5, color="rgba(255,255,255,0.2)")),
            hovertemplate=f"<b>{fuel}</b><br>Mileage: %{{x:,.0f}} km<br>Price: $%{{y:,.0f}}<extra></extra>"
        ))
    fig_scatter.update_layout(
        **layout_base,
        xaxis_title="Average Mileage (km)", yaxis_title="Price (USD)",
        yaxis_type=scale,
    )

    # Percentiles 
    pcts = [10, 25, 50, 75, 90]
    pct_vals = np.percentile(df["Price_USD"].dropna(), pcts)
    pct_divs = []
    for p, v in zip(pcts, pct_vals):
        pct_divs.append(html.Div([
            html.Span(f"P{p}", style={"color": "#7A90B8", "fontSize": "0.72rem", "width": "28px",
                                       "display": "inline-block"}),
            html.Div(style={
                "display": "inline-block", "height": "4px",
                "width": f"{p}%", "background": ACCENT,
                "borderRadius": "2px", "verticalAlign": "middle", "margin": "0 8px"
            }),
            html.Span(f"${v:,.0f}", style={"color": "#E8F0FF", "fontSize": "0.78rem", "fontWeight": "600"})
        ], style={"marginBottom": "10px", "display": "flex", "alignItems": "center"}))

    return (listings_txt, median_txt, mean_txt, mileage_txt, brand_txt,
            fig_hist, fig_year, fig_scatter, pct_divs)
