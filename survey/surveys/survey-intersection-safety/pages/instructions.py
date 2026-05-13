import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import time
from database import Database

# Database
db = Database('database.db')

# Register this page
dash.register_page(__name__, path='/instructions', name='Instructions')

# Page layout
def layout():
    return html.Div([
        # Main content container - centered and 80% width
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Instructions card
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Markdown(
                                """# Taakinstructies


## Wat u gaat doen

U krijgt een reeks kruispuntparen te zien, elk weergegeven door één
straatfoto. Geef bij elk paar aan **bij welk kruispunt de kans hoger
is dat een auto betrokken raakt bij een letsel- of dodelijk
verkeersongeval**.

Beschouw zowel enkelvoudige ongevallen (zoals controleverlies) als
botsingen op de rijbaan waarbij minstens één motorvoertuig betrokken is (inclusief met fietsers, voetgangers of andere weggebruikers). Puur materiële
schade telt niet mee.


## Hoe te beoordelen

Ga bij uw beoordeling uit van normaal, regelconform rijgedrag — het gaat om de inherente veiligheid van de inrichting, niet om incidenteel afwijkend gedrag van weggebruikers.

Baseer uw beoordeling uitsluitend op wat zichtbaar is in de foto. Eventuele voorkennis over de locatie of het kruispunt telt niet mee.

De verkeersintensiteitklasse wordt ter referentie getoond en betreft de tak die
zichtbaar is in de foto. Gebruik deze om te beoordelen of de zichtbare
inrichting passend is bij de belasting, niet als directe risicomaatstaf.

| Klasse | Drempelwaarde |
|---|---|
| Laag | < 1.000 voertuigen/dag |
| Middelmatig | 1.000 – 6.000 voertuigen/dag |
| Hoog | > 6.000 voertuigen/dag |

Let daarbij op de algehele indruk van de inrichting:

- Hoe duidelijk communiceert de lay-out de voorrangsrelaties?

- Hoe adequaat zijn de zichtlijnen?

- Hoe voorspelbaar is het verwachte gedrag van weggebruikers? 

- U hoeft geen afzonderlijke kenmerken te scoren of uw keuze toe te lichten. 

- Reageer op basis van uw eerste professionele indruk.


## Praktische opmerkingen

- Er is geen gelijkspeloptie: kies altijd het kruispunt dat u risicovoller acht, ook als het verschil klein lijkt.

- U kunt korte pauzes nemen tussen de vergelijkingen



**Klik op Doorgaan als u klaar bent om te beginnen.**
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
                            "Begin Activities",
                            id="instructions-button",
                            color="primary",
                            size="lg",
                            href="/act1/1#top",
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


# Callback to handle instructions button click - register time in database
@callback(
    Output('instructions-button', 'n_clicks'),
    Input('instructions-button', 'n_clicks'),
    State('user-store', 'data'),
    prevent_initial_call=True
)
def handle_instructions_click(n_clicks, user_data):
    if n_clicks and user_data:
        # Register time in database
        db.register_time(user_data['id'], 'instructions-button', time.time())
    
    return n_clicks
