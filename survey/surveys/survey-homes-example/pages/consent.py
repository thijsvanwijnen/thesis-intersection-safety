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
                                """## Informed Consent

I would like to invite you to participate in this research to understand preferences for residential properties and housing choices. This study is being carried out by Francisco Garrido-Valenzuela from TU Delft. The purpose of this research study is to explore how people evaluate and choose between different housing options. During the survey, you will be presented with different activities related to houses. This survey should take approximately **15-20 minutes** to complete.

As with any online activity, there is always a potential risk of a data breach. We will minimise all risks by keeping your responses confidential in secure TU Delft storage accessible only to the TU Delft research team. Additionally, the survey is designed to maintain your anonymity. Please do not provide personal information that could reveal your identity; if you do, that personal data will be deleted. Your responses to open-ended questions may be quoted in my student thesis.

Your responses to the closed questions may be made publicly available for potential further research, but they cannot be traced back to you. Responses to open questions will be deleted no later than one month after the completion of the project.

To participate in this research, you must be at least 18 years old. If any images or materials unexpectedly cause stress or anxiety, you are free to interrupt the survey at any time.

If you have any questions, feel free to contact me at f.garridov@tudelft.nl.

##### Thank you for your participation!
Francisco Garrido-Valenzuela
TU Delft
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
                                {"label": "I am older than 18 and I consent to participate in this study", "value": "agree"}
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
        tasks = db.get_data_for_respondent(respondent_id, {'act1': 8})
        
        # Store user data
        user_data = {'id': respondent_id, 'tasks': tasks}
        hrefs_data = {'next': {'/home': '/consent', '/consent': '/screening', '/screening': '/instructions', '/instructions': '/act1/1', '/act1/1': '/act1/2', '/act1/2': '/act1/3', '/act1/3': '/act1/4', '/act1/4': '/act1/5', '/act1/5': '/act1/6', '/act1/6': '/act1/7', '/act1/7': '/act1/8', '/act1/8': '/act2', '/act2': '/end'}}

        return user_data, hrefs_data
    
    return dash.no_update, dash.no_update
