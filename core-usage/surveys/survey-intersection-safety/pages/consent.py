import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import time
from database import Database

# Database
db = Database('database.db')

# Register this page
dash.register_page(__name__, path='/consent', name='Consent')

# Page layout
def layout():
    return html.Div([
        
        # Main content container - centered and 80% width
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Consent card
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Markdown(
                                """# Geïnformeerde toestemming

## Doel
Het doel van dit onderzoek is te bepalen of door experts beoordeelde visuele veiligheidsinformatie crashvoorspellingsmodellen voor stedelijke kruispunten kan verbeteren. Uw deelname helpt professionele verkeerskundige kennis om te zetten in een kwantitatief model.

## Wat wordt er van u gevraagd
- Paren straatfoto's van Rotterdamse kruispunten bekijken
- Aangeven welk kruispunt er veiliger uitziet
- Enkele verplichte screeningsvragen beantwoorden over uw professionele achtergrond
- Na de beoordelingstaak aanvullende achtergrondvragen beantwoorden
## Gegevensverwerking
- Alle antwoorden worden veilig opgeslagen op een TU Delft-server
- Gegevens worden anoniem verwerkt; individuele scores worden niet gerapporteerd
- Geagregeerde resultaten kunnen worden gepubliceerd in een academische scriptie en gerelateerde artikelen
- U kunt zich op elk moment zonder consequenties terugtrekken

## Contact
Voor vragen over dit onderzoek kunt u contact opnemen met:
**Thijs van Wijnen** — gvanwijnen@student.tudelft.nl
— TU Delft, Faculteit Technologie, Beleid en Management
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
                    
                    # Consent checkbox - inline with text
                    html.Div([
                        dbc.Checklist(
                            id="consent-checkbox",
                            options=[
                                {"label": "Ik heb de bovenstaande informatie gelezen, ik begrijp wat deelname inhoudt, en ik stem in met deelname aan dit onderzoek", "value": "agree"}
                            ],
                            value=[],
                            inline=True,
                            style={
                                "fontSize": "16px",
                                "fontWeight": "500"
                            }
                        )
                    ], style={
                        "textAlign": "center",
                        "marginBottom": "1.5rem"
                    }),
                    
                    # Continue button - disabled by default
                    html.Div([
                        dbc.Button(
                            "Continue",
                            id="consent-button",
                            color="primary",
                            size="lg",
                            disabled=True,
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


# Callback to enable/disable continue button and set href based on checkbox
@callback(
    [Output('consent-button', 'disabled'),
     Output('consent-button', 'href')],
    Input('consent-checkbox', 'value')
)
def toggle_continue_button(checkbox_value):
    is_disabled = "agree" not in (checkbox_value or [])
    href = "/screening#top" if not is_disabled else None
    return is_disabled, href


# Callback to handle consent button click - create user and load tasks
@callback(
    Output('user-store', 'data'),
    Output('hrefs-store', 'data'),
    Input('consent-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_consent_click(n_clicks):
    if n_clicks:
        # Create new user and get tasks
        respondent_id = db.create_new_respondent(time.time())
        tasks = db.get_data_for_respondent(respondent_id, {'act1': 36})
        
        # Store user data
        user_data = {'id': respondent_id, 'tasks': tasks}
        hrefs_data = {'next': {'/home': '/consent', '/consent': '/screening', '/screening': '/instructions', '/instructions': '/act1/1', '/act1/1': '/act1/2', '/act1/2': '/act1/3', '/act1/3': '/act1/4', '/act1/4': '/act1/5', '/act1/5': '/act1/6', '/act1/6': '/act1/7', '/act1/7': '/act1/8', '/act1/8': '/act1/9', '/act1/9': '/act1/10', '/act1/10': '/act1/11', '/act1/11': '/act1/12', '/act1/12': '/act1/13', '/act1/13': '/act1/14', '/act1/14': '/act1/15', '/act1/15': '/act1/16', '/act1/16': '/act1/17', '/act1/17': '/act1/18', '/act1/18': '/act1/19', '/act1/19': '/act1/20', '/act1/20': '/act1/21', '/act1/21': '/act1/22', '/act1/22': '/act1/23', '/act1/23': '/act1/24', '/act1/24': '/act1/25', '/act1/25': '/act1/26', '/act1/26': '/act1/27', '/act1/27': '/act1/28', '/act1/28': '/act1/29', '/act1/29': '/act1/30', '/act1/30': '/act1/31', '/act1/31': '/act1/32', '/act1/32': '/act1/33', '/act1/33': '/act1/34', '/act1/34': '/act1/35', '/act1/35': '/act1/36', '/act1/36': '/act2', '/act2': '/end'}}

        return user_data, hrefs_data
    
    return dash.no_update, dash.no_update
