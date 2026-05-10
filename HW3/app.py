import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap"
    ],
    suppress_callback_exceptions=True
)

server = app.server

SIDEBAR = dbc.Nav(
    [
        html.Div([
            html.Div("🚗", style={"fontSize": "2rem"}),
            html.H5("Jordan Cars", style={
                "fontFamily": "'Syne', sans-serif",
                "fontWeight": "800",
                "color": "#F0F4FF",
                "margin": "0",
                "fontSize": "1.1rem",
                "letterSpacing": "-0.02em"
            }),
            html.P("Market 2026", style={
                "color": "#8899BB",
                "fontSize": "0.7rem",
                "margin": "0",
                "letterSpacing": "0.1em",
                "textTransform": "uppercase"
            })
        ], style={"padding": "1.5rem 1rem 1rem", "borderBottom": "1px solid #1E2D4A"}),

        html.Div([
            dbc.NavLink([
                html.Span("01", style={"color": "#4D7EF7", "fontSize": "0.65rem", "fontWeight": "700", "display": "block", "marginBottom": "2px"}),
                "Pricing Overview"
            ], href="/", active="exact", style={
                "fontFamily": "'Syne', sans-serif", "fontWeight": "600", "fontSize": "0.85rem",
                "color": "#C5D0E8", "padding": "0.75rem 1rem", "borderRadius": "8px",
                "margin": "0.2rem 0", "transition": "all 0.2s"
            }),
            dbc.NavLink([
                html.Span("02", style={"color": "#4D7EF7", "fontSize": "0.65rem", "fontWeight": "700", "display": "block", "marginBottom": "2px"}),
                "Fuel & Brands"
            ], href="/fuel-brands", active="exact", style={
                "fontFamily": "'Syne', sans-serif", "fontWeight": "600", "fontSize": "0.85rem",
                "color": "#C5D0E8", "padding": "0.75rem 1rem", "borderRadius": "8px",
                "margin": "0.2rem 0", "transition": "all 0.2s"
            }),
            dbc.NavLink([
                html.Span("03", style={"color": "#4D7EF7", "fontSize": "0.65rem", "fontWeight": "700", "display": "block", "marginBottom": "2px"}),
                "Geography"
            ], href="/geography", active="exact", style={
                "fontFamily": "'Syne', sans-serif", "fontWeight": "600", "fontSize": "0.85rem",
                "color": "#C5D0E8", "padding": "0.75rem 1rem", "borderRadius": "8px",
                "margin": "0.2rem 0", "transition": "all 0.2s"
            }),
        ], style={"padding": "0.75rem 0.5rem", "flex": "1"}),

        html.Div([
            html.P("Data: Kaggle · Jordan 2026", style={
                "color": "#445577", "fontSize": "0.65rem", "margin": "0", "textAlign": "center"
            })
        ], style={"padding": "1rem", "borderTop": "1px solid #1E2D4A"})
    ],
    vertical=True,
    pills=True,
    style={
        "width": "180px",
        "minHeight": "100vh",
        "background": "#0A1628",
        "position": "fixed",
        "top": 0,
        "left": 0,
        "display": "flex",
        "flexDirection": "column",
        "zIndex": 1000,
        "boxShadow": "4px 0 24px rgba(0,0,0,0.4)"
    }
)

app.layout = html.Div([
    SIDEBAR,
    html.Div(
        dash.page_container,
        style={
            "marginLeft": "180px",
            "minHeight": "100vh",
            "background": "#0D1B2E",
            "padding": "0"
        }
    )
])

if __name__ == "__main__":
    app.run(debug=True, port=8050)