import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_jordan_data

dash.register_page(__name__, path="/fuel-brands", name="Fuel & Brands")

CARD_STYLE = {
    "background": "#0F2040", "border": "1px solid #1A3060",
    "borderRadius": "12px", "padding": "1.25rem",
}
TITLE_STYLE = {
    "fontFamily": "'Syne', sans-serif", "fontWeight": "700",
    "color": "#E8F0FF", "fontSize": "0.85rem", "letterSpacing": "0.05em",
    "textTransform": "uppercase", "marginBottom": "1rem",
}
PLOT_BG = PAPER_BG = "#0F2040"
FONT_COLOR = "#C5D0E8"
GRID_COLOR = "#1A3060"
ACCENT = "#4D7EF7"
FUEL_COLORS = {
    "Gasoline": "#636EFA", "Diesel": "#EF553B",
    "Hybrid": "#00CC96", "Electric": "#AB63FA", "Other": "#FFA15A"
}
FUEL_ORDER = ["Gasoline", "Diesel", "Hybrid", "Electric", "Other"]

layout = html.Div([
    
    html.Div([
        html.P("JORDAN CARS MARKET 2026", style={
            "color": ACCENT, "fontSize": "0.7rem", "fontWeight": "700",
            "letterSpacing": "0.15em", "margin": "0", "fontFamily": "'Syne', sans-serif"
        }),
        html.H1("Fuel & Brands", style={
            "fontFamily": "'Syne', sans-serif", "fontWeight": "800",
            "color": "#F0F4FF", "margin": "0.25rem 0 0.5rem",
            "fontSize": "2rem", "letterSpacing": "-0.03em"
        }),
        html.P("Fuel transition over time, brand landscape and price comparison",
               style={"color": "#7A90B8", "margin": 0, "fontSize": "0.85rem"})
    ], style={"padding": "2rem 2rem 1.5rem"}),


    html.Div([
        html.Div([
            html.Label("Top N Brands", style={"color": "#7A90B8", "fontSize": "0.7rem",
                                               "textTransform": "uppercase", "letterSpacing": "0.08em",
                                               "display": "block", "marginBottom": "6px"}),
            dcc.Slider(id="p2-topn", min=5, max=15, step=1, value=10,
                       marks={n: {"label": str(n), "style": {"color": "#7A90B8", "fontSize": "0.65rem"}}
                              for n in range(5, 16, 2)},
                       tooltip={"placement": "bottom", "always_visible": False})
        ], style={"flex": "1", "minWidth": "220px"}),

        html.Div([
            html.Label("Year Range (Fuel Trend)", style={"color": "#7A90B8", "fontSize": "0.7rem",
                                                          "textTransform": "uppercase", "letterSpacing": "0.08em",
                                                          "display": "block", "marginBottom": "6px"}),
            dcc.RangeSlider(id="p2-year", min=2000, max=2026, step=1, value=[2000, 2026],
                            marks={y: {"label": str(y), "style": {"color": "#7A90B8", "fontSize": "0.65rem"}}
                                   for y in range(2000, 2027, 5)},
                            tooltip={"placement": "bottom", "always_visible": False})
        ], style={"flex": "1.5", "minWidth": "280px"}),

        html.Div([
            html.Label("Chart Type (Brands)", style={"color": "#7A90B8", "fontSize": "0.7rem",
                                                       "textTransform": "uppercase", "letterSpacing": "0.08em",
                                                       "display": "block", "marginBottom": "6px"}),
            dcc.Dropdown(
                id="p2-chart-type",
                options=[{"label": "Listings Count", "value": "count"},
                         {"label": "Median Price", "value": "median"},
                         {"label": "Mean Price", "value": "mean"}],
                value="count", clearable=False,
                style={"background": "#0A1628", "color": "#C5D0E8",
                       "border": "1px solid #1A3060", "fontSize": "0.82rem"}
            )
        ], style={"width": "180px"}),
    ], style={
        "display": "flex", "gap": "1.5rem", "flexWrap": "wrap",
        "alignItems": "flex-end", "padding": "0 2rem 1.5rem", "background": "#0D1B2E"
    }),

    # Row 1: Fuel pie + Fuel trend
    html.Div([
        html.Div([
            html.Div("Fuel Type Market Share", style=TITLE_STYLE),
            dcc.Graph(id="p2-fuel-pie", config={"displayModeBar": False},
                      style={"height": "300px"})
        ], style={**CARD_STYLE, "flex": "1"}),

        html.Div([
            html.Div("Fuel Type Adoption Over Years (Jordan)", style=TITLE_STYLE),
            dcc.Graph(id="p2-fuel-area", config={"displayModeBar": False},
                      style={"height": "300px"})
        ], style={**CARD_STYLE, "flex": "2"}),
    ], style={"display": "flex", "gap": "1rem", "padding": "0 2rem 1rem"}),

    # Row 2: Brand bar + Brand bubble
    html.Div([
        html.Div([
            html.Div("Top Brands", style=TITLE_STYLE),
            dcc.Graph(id="p2-brand-bar", config={"displayModeBar": False},
                      style={"height": "360px"})
        ], style={**CARD_STYLE, "flex": "1"}),

        html.Div([
            html.Div([
                html.Span("Brand × Year  ", style={**TITLE_STYLE, "display": "inline", "marginBottom": 0}),
                html.Span("(bubble = listings, select brand below)",
                          style={"color": "#5A7099", "fontSize": "0.72rem"})
            ], style={"marginBottom": "1rem"}),
            html.Div([
                dcc.Dropdown(
                    id="p2-brand-select",
                    placeholder="Filter by brand…", multi=True,
                    style={"background": "#0A1628", "color": "#C5D0E8",
                           "border": "1px solid #1A3060", "fontSize": "0.8rem",
                           "marginBottom": "0.75rem"}
                ),
            ]),
            dcc.Graph(id="p2-brand-bubble", config={"displayModeBar": False},
                      style={"height": "320px"})
        ], style={**CARD_STYLE, "flex": "2"}),
    ], style={"display": "flex", "gap": "1rem", "padding": "0 2rem 2rem"}),

], style={"background": "#0D1B2E", "minHeight": "100vh"})


@callback(
    Output("p2-fuel-pie", "figure"),
    Output("p2-fuel-area", "figure"),
    Output("p2-brand-bar", "figure"),
    Output("p2-brand-bubble", "figure"),
    Output("p2-brand-select", "options"),
    Input("p2-topn", "value"),
    Input("p2-year", "value"),
    Input("p2-chart-type", "value"),
    Input("p2-brand-select", "value"),
)
def update_page2(topn, year_range, chart_type, selected_brands):
    df = load_jordan_data()

    layout_base = dict(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR, family="DM Sans, sans-serif", size=11),
    )


    # Fuel pie
    fuel_pct = (
        df["Fuel_Type"].value_counts(normalize=True)
        .mul(100).round(1)
        .reindex(FUEL_ORDER, fill_value=0)
        .reset_index()
    )
    fuel_pct.columns = ["Fuel_Type", "Pct"]
    fig_pie = go.Figure(go.Pie(
        labels=fuel_pct["Fuel_Type"],
        values=fuel_pct["Pct"],
        hole=0.5,
        marker_colors=[FUEL_COLORS.get(f, "#888") for f in fuel_pct["Fuel_Type"]],
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
        textfont=dict(size=11, color="#E8F0FF"),
        insidetextorientation="radial"
    ))
    fig_pie.update_layout(
        **layout_base,
        showlegend=True,
        legend=dict(orientation="v", x=0.85, y=0.5, bgcolor="rgba(0,0,0,0)",
                    font=dict(size=10, color=FONT_COLOR)),
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(text="Fuel<br>Share", x=0.5, y=0.5,
                          font=dict(size=11, color="#7A90B8"), showarrow=False)]
    )

    #Fuel area
    df_area = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
    fuel_year = (
        df_area.groupby(["Year", "Fuel_Type"]).size()
        .reset_index(name="Count")
    )
    fuel_year["Pct"] = fuel_year.groupby("Year")["Count"].transform(lambda x: x / x.sum() * 100)

    fig_area = px.area(
        fuel_year, x="Year", y="Pct", color="Fuel_Type",
        labels={"Pct": "% Listings", "Year": "Model Year", "Fuel_Type": "Fuel"},
        color_discrete_map=FUEL_COLORS,
        category_orders={"Fuel_Type": FUEL_ORDER}
    )
    fig_area.update_layout(
        **layout_base,
        xaxis_title="Model Year", yaxis_title="% of Listings",
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        legend=dict(orientation="h", y=-0.2, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=9))
    )

    # Brand bar
    top_brands = df["Brand"].value_counts().head(topn).index.tolist()
    df_brands = df[df["Brand"].isin(top_brands)]

    if chart_type == "count":
        brand_vals = df_brands["Brand"].value_counts().reindex(top_brands).reset_index()
        brand_vals.columns = ["Brand", "Value"]
        xtitle = "Number of Listings"
    else:
        agg_fn = chart_type  # "median" or "mean"
        brand_vals = df_brands.groupby("Brand")["Price_USD"].agg(agg_fn).reindex(top_brands).reset_index()
        brand_vals.columns = ["Brand", "Value"]
        xtitle = f"{agg_fn.title()} Price (USD)"

    brand_vals = brand_vals.sort_values("Value", ascending=True)

    fig_bar = go.Figure(go.Bar(
        x=brand_vals["Value"], y=brand_vals["Brand"],
        orientation="h",
        marker=dict(
            color=brand_vals["Value"],
            colorscale=[[0, "#1A3060"], [1, ACCENT]],
            showscale=False
        ),
        hovertemplate="%{y}: %{x:,.0f}<extra></extra>"
    ))
    fig_bar.update_layout(
        **layout_base,
        xaxis=dict(title=xtitle, gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=100, r=20, t=10, b=40),
    )

    # Brand bubble 
    df_bub = df[df["Brand"].isin(top_brands)]
    if selected_brands:
        df_bub = df_bub[df_bub["Brand"].isin(selected_brands)]

    bub_data = (
        df_bub[df_bub["Year"] >= 2005]
        .groupby(["Brand", "Year"])
        .agg(Median_Price=("Price_USD", "median"), Count=("Price_USD", "count"))
        .reset_index()
    )

    palette = px.colors.qualitative.Vivid
    brand_color_map = {b: palette[i % len(palette)] for i, b in enumerate(top_brands)}

    fig_bub = go.Figure()
    for brand in bub_data["Brand"].unique():
        sub = bub_data[bub_data["Brand"] == brand]
        # Logarithmic scale for bubble size 
        bubble_size = np.log1p(sub["Count"]) * 8
        fig_bub.add_trace(go.Scatter(
            x=sub["Year"], y=sub["Median_Price"],
            mode="markers", name=brand,
            marker=dict(
                size=bubble_size, sizemode="area",
                color=brand_color_map.get(brand, ACCENT),
                opacity=0.75,
                line=dict(width=1, color="rgba(255,255,255,0.2)")
            ),
            hovertemplate=(
                f"<b>{brand}</b><br>Year: %{{x}}<br>"
                "Median: $%{y:,.0f}<br>Listings: %{customdata}<extra></extra>"
            ),
            customdata=sub["Count"]
        ))

    fig_bub.update_layout(
        **layout_base,
        xaxis=dict(title="Model Year", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(title="Median Price (USD)", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        margin=dict(l=50, r=20, t=10, b=40),
    )

    # Brand select options
    brand_options = [{"label": b, "value": b} for b in top_brands]

    return fig_pie, fig_area, fig_bar, fig_bub, brand_options
