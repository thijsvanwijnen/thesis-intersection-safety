import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

# Register this page
dash.register_page(__name__, path='/fullquota', name='Full Quota')

# Page layout
def layout():
    return html.Div([
        # Main content container - centered and 80% width
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Full quota message card
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Markdown(
                                """# Bedankt voor uw interesse

Helaas is dit onderzoek voorbehouden aan professionals met een achtergrond in
verkeerskunde of verkeersveiligheidsontwerp. Uw profiel voldoet niet aan de
deelnamecriteria voor dit specifieke onderzoek.

Hartelijk dank voor uw tijd.
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
                    })
                    
                ], width={"size": 10, "offset": 1})  # 80% width (10/12) with 1 column offset on each side
            ])
        ], fluid=True, style={"minHeight": "80vh", "backgroundColor": "#f8f9fa"})  # Light gray background
    ])