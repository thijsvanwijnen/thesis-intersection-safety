import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

# Register this page
dash.register_page(__name__, path='/end', name='End')

# Page layout
def layout():
    return html.Div([
        # Main content container - centered and 80% width
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Progress indicator
                    html.Div([
                        dbc.Progress(
                            value= 100,
                            label="100%",
                            style={"height": "15px", "fontSize": "10px"},
                            color="primary"
                        )
                    ], style={"marginBottom": "2rem", "marginTop": "0.5rem"}),

                    # End message card
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Markdown(
                                """# Bedankt voor uw deelname

## Uw bijdrage
U heeft de paarsgewijze vergelijkingssessie voltooid. Uw expertbeoordelingen
vormen de basis van dit onderzoek en worden zeer gewaardeerd.

## Wat er verder gebeurt
Uw antwoorden worden gebruikt om een continue veiligheidsscore per kruispunt te schatten via een Bradley-Terry-model. Vervolgens wordt onderzocht of het toevoegen van deze scores een meerwaarde heeft voor crashvoorspellingsmodellen voor Rotterdam.

## Resultaten
Als u een samenvatting van de onderzoeksresultaten wilt ontvangen zodra de scriptie
is afgerond, stuur dan een e-mail naar:
**gvanwijnen@student.tudelft.nl**

## Vragen
Voor vragen over dit onderzoek kunt u contact opnemen met de onderzoeker gvanwijnen@tudelft.nl.

**Hartelijk dank voor uw waardevolle bijdrage.**
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
