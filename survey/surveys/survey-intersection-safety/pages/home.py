import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

# Register this page
dash.register_page(__name__, path='/', name='Home')

# Page layout
def layout():
    return html.Div([
        # Main content container - centered and 80% width
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Welcome card
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Markdown(
                                """# Welkom
U neemt deel aan een expertonderzoek van **TU Delft** en **Gemeente Rotterdam** over visuele veiligheidsbeoordeling van Rotterdamse kruispunten.
- Duurt ongeveer **20 minuten**
- U beoordeelt **40 kruispuntparen**
- Geen goede of foute antwoorden — uw professionele oordeel staat centraal
- Klik op **Start onderzoek** om verder te gaan.
""",
                                style={
                                    "fontSize": "16px",
                                    "lineHeight": "1.6",
                                    "color": "#333",
                                    "textAlign": "justify"
                                }
                            )
                        ], style={"padding": "2rem"})
                    ], style={
                        "boxShadow": "0 4px 8px rgba(0,0,0,0.1)",
                        "borderRadius": "12px",
                        "border": "none",
                        "marginTop": "2rem",
                        "marginBottom": "2rem"
                    }),
                    
                    # Begin button - centered below the card
                    html.Div([
                        dbc.Button(
                            "Start onderzoek",
                            id="home-button",
                            color="primary",
                            size="lg",
                            href="/consent#top",
                            style={
                                "fontSize": "18px",
                                "fontWeight": "bold",
                                "padding": "12px 40px",
                                "borderRadius": "8px",
                                "boxShadow": "0 2px 4px rgba(0,0,0,0.2)"
                            }
                        )
                    ], style={
                        "textAlign": "center",
                        "marginBottom": "3rem"
                    })
                    
                ], width={"size": 10, "offset": 1})  # 80% width (10/12) with 1 column offset on each side
            ])
        ], fluid=True, style={"minHeight": "80vh", "backgroundColor": "#f8f9fa"})  # Light gray background
    ])
