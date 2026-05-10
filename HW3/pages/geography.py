import dash
from dash import dcc, html, callback, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json, requests, os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_jordan_data

dash.register_page(__name__, path="/geography", name="Geography")

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

CITY_COORDS = {
    "Amman":     [31.945367, 35.928372],
    "Irbid":     [32.556847, 35.847896],
    "Zarqa":     [32.072915, 36.097947],
    "Ramtha":    [32.558889, 36.006944],
    "Salt":      [32.039167, 35.727222],
    "Madaba":    [31.716667, 35.800000],
    "Aqaba":     [29.531917, 35.005314],
    "Mafraq":    [32.342222, 36.208333],
    "Jerash":    [32.274167, 35.896389],
    "Karak":     [31.185000, 35.704722],
    "Ajloun":    [32.333333, 35.750000],
    "Tafilah":   [30.833333, 35.600000],
    "Ma'an":     [30.196667, 35.734167],
    "Al Mafraq": [32.342222, 36.208333],
}

CITY_TO_GOV = {
    "Amman": "Amman", "Irbid": "Irbid", "Zarqa": "Zarqa",
    "Ramtha": "Irbid", "Salt": "Balqa", "Madaba": "Madaba",
    "Aqaba": "Aqaba", "Mafraq": "Mafraq", "Al Mafraq": "Mafraq",
    "Jerash": "Jarash", "Karak": "Karak", "Ajloun": "Ajlun",
    "Tafilah": "Tafilah", "Ma'an": "Ma`an",
}

_geojson_cache = {}

def _load_geojson():
    if "data" in _geojson_cache:
        return _geojson_cache["data"]
    url = (
        "https://raw.githubusercontent.com/apache/superset/master/"
        "superset-frontend/plugins/legacy-plugin-chart-country-map/"
        "src/countries/jordan.geojson"
    )
    try:
        r = requests.get(url, timeout=8)
        data = r.json()
    except Exception:
        data = {"type": "FeatureCollection", "features": []}
    _geojson_cache["data"] = data
    return data


def _build_city_stats(df, stat):
    stats = (
        df.groupby("City")
        .agg(
            Listings=("Price_USD", "count"),
            Median_Price=("Price_USD", "median"),
            Mean_Price=("Price_USD", "mean"),
            Median_Mileage=("Mileage_Avg", "median"),
            Median_Year=("Year", "median"),
        )
        .reset_index()
    )
    total = stats["Listings"].sum()
    stats["Pct"] = (stats["Listings"] / total * 100).round(1)
    stats["lat"] = stats["City"].map(lambda c: CITY_COORDS.get(c, [31.2, 36.0])[0])
    stats["lon"] = stats["City"].map(lambda c: CITY_COORDS.get(c, [31.2, 36.0])[1])
    stats["Governorate"] = stats["City"].map(CITY_TO_GOV).fillna("Other")
    stats["Price_Display"] = stats["Median_Price"] if stat == "median" else stats["Mean_Price"]
    return stats


layout = html.Div([
    # Header
    html.Div([
        html.P("JORDAN CARS MARKET 2026", style={
            "color": ACCENT, "fontSize": "0.7rem", "fontWeight": "700",
            "letterSpacing": "0.15em", "margin": "0", "fontFamily": "'Syne', sans-serif"
        }),
        html.H1("Geography", style={
            "fontFamily": "'Syne', sans-serif", "fontWeight": "800",
            "color": "#F0F4FF", "margin": "0.25rem 0 0.5rem",
            "fontSize": "2rem", "letterSpacing": "-0.03em"
        }),
        html.P("Where are cars listed in Jordan? How do prices vary by city and governorate?",
               style={"color": "#7A90B8", "margin": 0, "fontSize": "0.85rem"})
    ], style={"padding": "2rem 2rem 1.5rem"}),

    # Filter bar
    html.Div([
        html.Div([
            html.Label("Price Statistic", style={
                "color": "#7A90B8", "fontSize": "0.7rem",
                "textTransform": "uppercase", "letterSpacing": "0.08em",
                "display": "block", "marginBottom": "6px"
            }),
            dcc.RadioItems(
                id="geo-stat",
                options=[{"label": " Median", "value": "median"},
                         {"label": " Mean",   "value": "mean"}],
                value="median", inline=True,
                labelStyle={"color": "#C5D0E8", "fontSize": "0.82rem",
                            "marginRight": "1rem"},
                inputStyle={"accentColor": ACCENT, "marginRight": "4px"}
            ),
        ]),

        html.Div([
            html.Label("Map Bubble Scale", style={
                "color": "#7A90B8", "fontSize": "0.7rem",
                "textTransform": "uppercase", "letterSpacing": "0.08em",
                "display": "block", "marginBottom": "6px"
            }),
            dcc.RadioItems(
                id="geo-bubble-scale",
                options=[{"label": " Linear", "value": "linear"},
                         {"label": " Log",    "value": "log"}],
                value="log", inline=True,
                labelStyle={"color": "#C5D0E8", "fontSize": "0.82rem",
                            "marginRight": "1rem"},
                inputStyle={"accentColor": ACCENT, "marginRight": "4px"}
            ),
        ]),

        html.Div([
            html.Label("Min. Listings (City Bar)", style={
                "color": "#7A90B8", "fontSize": "0.7rem",
                "textTransform": "uppercase", "letterSpacing": "0.08em",
                "display": "block", "marginBottom": "6px"
            }),
            dcc.Slider(
                id="geo-min-listings", min=1, max=50, step=1, value=5,
                marks={n: {"label": str(n), "style": {"color": "#7A90B8", "fontSize": "0.65rem"}}
                       for n in [1, 10, 20, 30, 50]},
                tooltip={"placement": "bottom", "always_visible": False}
            )
        ], style={"flex": "1", "minWidth": "220px"}),
    ], style={
        "display": "flex", "gap": "2rem", "flexWrap": "wrap",
        "alignItems": "flex-end", "padding": "0 2rem 1.5rem",
        "background": "#0D1B2E"
    }),

    # Row 1: Choropleth map (full width)
    html.Div([
        html.Div([
            html.Div("Listings & Prices by Governorate", style=TITLE_STYLE),
            dcc.Graph(id="geo-choropleth", config={"displayModeBar": False},
                      style={"height": "430px"})
        ], style=CARD_STYLE),
    ], style={"padding": "0 2rem 1rem"}),

    # Row 2: City listings bar + City price bar
    html.Div([
        html.Div([
            html.Div("Top Cities by Number of Listings", style=TITLE_STYLE),
            dcc.Graph(id="geo-city-listings", config={"displayModeBar": False},
                      style={"height": "340px"})
        ], style={**CARD_STYLE, "flex": "1"}),

        html.Div([
            html.Div(id="geo-city-price-title", style=TITLE_STYLE),
            dcc.Graph(id="geo-city-price", config={"displayModeBar": False},
                      style={"height": "340px"})
        ], style={**CARD_STYLE, "flex": "1"}),
    ], style={"display": "flex", "gap": "1rem", "padding": "0 2rem 1rem"}),

    # Row 3: Price distribution box by city
    html.Div([
        html.Div([
            html.Div("Price Distribution by Major City", style=TITLE_STYLE),
            html.Div([
                dcc.Dropdown(
                    id="geo-city-select",
                    placeholder="Select cities to compare…",
                    multi=True,
                    style={"background": "#0A1628", "color": "#C5D0E8",
                           "border": "1px solid #1A3060", "fontSize": "0.8rem",
                           "marginBottom": "0.75rem"}
                ),
            ]),
            dcc.Graph(id="geo-boxplot", config={"displayModeBar": False},
                      style={"height": "320px"})
        ], style=CARD_STYLE),
    ], style={"padding": "0 2rem 2rem"}),

], style={"background": "#0D1B2E", "minHeight": "100vh"})


@callback(
    Output("geo-choropleth",      "figure"),
    Output("geo-city-listings",   "figure"),
    Output("geo-city-price",      "figure"),
    Output("geo-city-price-title","children"),
    Output("geo-boxplot",         "figure"),
    Output("geo-city-select",     "options"),
    Input("geo-stat",             "value"),
    Input("geo-bubble-scale",     "value"),
    Input("geo-min-listings",     "value"),
    Input("geo-city-select",      "value"),
)
def update_geo(stat, bubble_scale, min_listings, selected_cities):
    df = load_jordan_data()
    city_stats = _build_city_stats(df, stat)
    geojson = _load_geojson()

    layout_base = dict(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR, family="DM Sans, sans-serif", size=11),
    )

    #Governorate aggregating
    gov_stats = (
        city_stats.groupby("Governorate")
        .agg(Listings=("Listings", "sum"),
             Price=("Price_Display", "median"))
        .reset_index()
    )


    fig_map = go.Figure()

    if geojson["features"]:
        fig_map.add_trace(go.Choropleth(
            geojson=geojson,
            locations=gov_stats["Governorate"],
            z=gov_stats["Listings"],
            featureidkey="properties.NAME_1",
            colorscale=[
                [0.0, "#0F2040"],
                [0.1, "#1A3A70"],
                [0.3, "#1E5FAA"],
                [0.6, "#2878D4"],
                [1.0, "#4D7EF7"],
            ],
            marker_line_color="#0D1B2E",
            marker_line_width=1.5,
            colorbar=dict(
                title=dict(text="Listings", font=dict(color=FONT_COLOR, size=10)),
                tickfont=dict(color=FONT_COLOR, size=9),
                bgcolor=PAPER_BG,
                bordercolor="#1A3060",
                len=0.6, x=1.01,
            ),
            customdata=gov_stats[["Governorate", "Listings", "Price"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Listings: %{customdata[1]:,}<br>"
                f"{stat.title()} Price: $%{{customdata[2]:,.0f}}"
                "<extra></extra>"
            ),
        ))

    # Bubble scatter on top (sized by listings, log or linear)
    city_map = city_stats[city_stats["Listings"] >= 3].copy()
    if bubble_scale == "log":
        city_map["BubbleSize"] = np.log1p(city_map["Listings"]) * 6
    else:
        city_map["BubbleSize"] = np.sqrt(city_map["Listings"]) * 2.5

    fig_map.add_trace(go.Scattergeo(
        lat=city_map["lat"],
        lon=city_map["lon"],
        mode="markers+text",
        text=city_map["City"],
        textposition="top center",
        textfont=dict(size=8, color="#C5D0E8"),
        marker=dict(
            size=city_map["BubbleSize"],
            color=city_map["Price_Display"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(
                title=dict(text=f"{stat.title()} $", font=dict(color=FONT_COLOR, size=10)),
                tickfont=dict(color=FONT_COLOR, size=9),
                bgcolor=PAPER_BG,
                bordercolor="#1A3060",
                len=0.6, x=1.12,
            ),
            opacity=0.85,
            line=dict(color="#0D1B2E", width=1),
        ),
        customdata=city_map[["City", "Listings", "Price_Display", "Median_Mileage", "Pct"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Listings: %{customdata[1]:,} (%{customdata[4]:.1f}%)<br>"
            f"{stat.title()} Price: $%{{customdata[2]:,.0f}}<br>"
            "Median Mileage: %{customdata[3]:,.0f} km"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    fig_map.update_layout(
        **layout_base,
        geo=dict(
            scope="asia",
            center=dict(lat=31.2, lon=36.5),
            projection_scale=12,
            showland=True, landcolor="#0A1628",
            showocean=True, oceancolor="#071018",
            showlakes=False,
            showcountries=True, countrycolor="#1A3060",
            showframe=False,
            bgcolor=PAPER_BG,
        ),
        margin=dict(l=0, r=60, t=0, b=0),
    )

    #City listings bar
    top_cities = city_stats.nlargest(12, "Listings").sort_values("Listings", ascending=True)

    fig_listings = go.Figure(go.Bar(
        x=top_cities["Listings"],
        y=top_cities["City"],
        orientation="h",
        text=top_cities["Listings"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(size=9, color=FONT_COLOR),
        marker=dict(
            color=top_cities["Listings"],
            colorscale=[[0, "#1A3060"], [1, ACCENT]],
            showscale=False,
        ),
        hovertemplate="%{y}: %{x:,} listings<extra></extra>",
    ))
    fig_listings.update_layout(
        **layout_base,
        xaxis=dict(title="Listings", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=80, r=50, t=10, b=40),
    )

    # City price bar (median OR mean, filtered by min listings)
    price_col = "Median_Price" if stat == "median" else "Mean_Price"
    city_price = (
        city_stats[city_stats["Listings"] >= min_listings]
        .nlargest(12, price_col)
        .sort_values(price_col, ascending=True)
    )
    price_title = f"Top Cities by {stat.title()} Price (min {min_listings} listings)"

    fig_price = go.Figure(go.Bar(
        x=city_price[price_col],
        y=city_price["City"],
        orientation="h",
        text=city_price[price_col].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(size=9, color=FONT_COLOR),
        marker=dict(
            color=city_price[price_col],
            colorscale=[[0, "#1A3A50"], [1, "#00D4AA"]],
            showscale=False,
        ),
        hovertemplate="%{y}: $%{x:,.0f}<extra></extra>",
    ))
    fig_price.update_layout(
        **layout_base,
        xaxis=dict(title=f"{stat.title()} Price (USD)", gridcolor=GRID_COLOR,
                   zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=80, r=70, t=10, b=40),
    )

    #Box plot by selected cities
    all_cities = sorted(city_stats[city_stats["Listings"] >= 5]["City"].tolist())
    city_options = [{"label": c, "value": c} for c in all_cities]

    default_cities = ["Amman", "Zarqa", "Irbid", "Salt", "Madaba", "Jerash", "Karak"]
    cities_to_show = selected_cities if selected_cities else default_cities
    df_box = df[df["City"].isin(cities_to_show)]

    palette = [
        "#4D7EF7", "#00CC96", "#FF6B4D", "#AB63FA",
        "#F7C84D", "#00D4AA", "#FF4D6B", "#63D4F7",
        "#B44DFF", "#FFB347", "#4DFFB4", "#FF4DB3",
    ]
    fig_box = go.Figure()
    for i, city in enumerate(cities_to_show):
        sub = df_box[df_box["City"] == city]["Price_USD"]
        if sub.empty:
            continue
        color = palette[i % len(palette)]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig_box.add_trace(go.Box(
            y=sub, name=city,
            marker_color=color,
            line_color=color,
            fillcolor=f"rgba({r},{g},{b},0.25)",
            boxmean=True,
            hovertemplate=f"<b>{city}</b><br>Price: $%{{y:,.0f}}<extra></extra>",
        ))

    fig_box.update_layout(
        **layout_base,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Price (USD)", gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        showlegend=False,
        margin=dict(l=60, r=20, t=10, b=40),
        annotations=[dict(
            x=1, y=1, xref="paper", yref="paper", showarrow=False,
            text="Box = IQR · Line = median · Dot = mean",
            font=dict(size=9, color="#5A7099"),
            xanchor="right", yanchor="top"
        )]
    )

    return fig_map, fig_listings, fig_price, price_title, fig_box, city_options
