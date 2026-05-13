import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import time
from database import Database

# Database
db = Database('database.db')

# Register this page
dash.register_page(__name__, path='/screening', name='Screening')

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
                                """# Screeningsvragen

Beantwoord de onderstaande vragen. Alleen deelnemers met een professionele achtergrond in verkeerskunde of verkeersveiligheidsontwerp komen in aanmerking voor dit onderzoek.
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
                    
                    # List of Screening questions
                    html.Div([
                        dbc.Card([
    dbc.CardBody([
        # Question text
        dbc.Row([
            dbc.Col([
                dbc.Label(
                    "Wat omschrijft uw huidige professionele rol het beste? *",
                    html_for="question-1",
                    style={
                        "fontWeight": "bold",
                        "color": "darkblue",
                        "fontSize": "16px",
                        "marginBottom": "1rem"
                    }
                )
            ])
        ]),
        
        # Answer options (dropdown)
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="question-1",
                    placeholder="Please select an option...",
                    options=[
                        
                        {"label": "Verkeerskundig ingenieur / wegontwerper", "value": "1"},
                        
                        {"label": "Verkeersveiligheidsspecialist / -auditor", "value": "2"},
                        
                        {"label": "Stedenbouwkundige (met focus op verkeersveiligheid)", "value": "3"},
                        
                        {"label": "Beleidsadviseur (zonder technische achtergrond)", "value": "4"},
                        
                        {"label": "Verkeersveiligheidsadviseur", "value": "5"},
                        
                        {"label": "Anders", "value": "6"}
                        
                    ],
                    style={"fontSize": "14px"},
                  # required=True
                )
            ])
        ])
    ], style={"padding": "1.5rem"})
], style={
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    "borderRadius": "8px", 
    "border": "none",
    "marginBottom": "1.5rem"
}),
        dbc.Card([
    dbc.CardBody([
        # Question text
        dbc.Row([
            dbc.Col([
                dbc.Label(
                    "Voor welke organisatie werkt u momenteel? *",
                    html_for="question-2",
                    style={
                        "fontWeight": "bold",
                        "color": "darkblue",
                        "fontSize": "16px",
                        "marginBottom": "1rem"
                    }
                )
            ])
        ]),
        
        # Answer options (dropdown)
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="question-2",
                    placeholder="Please select an option...",
                    options=[
                        
                        {"label": "Gemeente Rotterdam", "value": "1"},
                        
                        {"label": "Andere gemeente", "value": "2"},
                        
                        {"label": "Provincie", "value": "3"},
                        
                        {"label": "Rijkswaterstaat", "value": "4"},
                        
                        {"label": "Ingenieursbureau", "value": "5"},
                        
                        {"label": "Kennisinstituut / universiteit", "value": "6"},
                        
                        {"label": "Wil ik niet zeggen", "value": "7"}
                        
                    ],
                    style={"fontSize": "14px"},
                  # required=True
                )
            ])
        ])
    ], style={"padding": "1.5rem"})
], style={
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    "borderRadius": "8px", 
    "border": "none",
    "marginBottom": "1.5rem"
}),
        dbc.Card([
    dbc.CardBody([
        # Question text
        dbc.Row([
            dbc.Col([
                dbc.Label(
                    "Hoeveel jaar professionele ervaring heeft u in verkeersveiligheid of wegontwerp? *",
                    html_for="question-3",
                    style={
                        "fontWeight": "bold",
                        "color": "darkblue",
                        "fontSize": "16px",
                        "marginBottom": "1rem"
                    }
                )
            ])
        ]),
        
        # Answer options (dropdown)
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="question-3",
                    placeholder="Please select an option...",
                    options=[
                        
                        {"label": "Minder dan 2 jaar", "value": "1"},
                        
                        {"label": "2–5 jaar", "value": "2"},
                        
                        {"label": "6–10 jaar", "value": "3"},
                        
                        {"label": "Meer dan 10 jaar", "value": "4"}
                        
                    ],
                    style={"fontSize": "14px"},
                  # required=True
                )
            ])
        ])
    ], style={"padding": "1.5rem"})
], style={
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    "borderRadius": "8px", 
    "border": "none",
    "marginBottom": "1.5rem"
})
                    ], style={"marginBottom": "2rem"}),

                    # Navigation buttons
                    html.Div([
                        dbc.Button(
                            "Continue",
                            id="screening-button",
                            color="primary",
                            size="lg",
                            disabled=True,
                            href="/instructions#top",
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


# Callback to enable/disable continue button based on all screening questions being answered
@callback(
    [Output('screening-button', 'disabled'),
     Output('screening-button', 'href')],
     State('hrefs-store', 'data'),
    [Input(f'question-{i}', 'value') for i in range(1, 3 + 1)],
    prevent_initial_call=True
)
def toggle_continue_button(hrefs, *question_values):
    # Check if all questions have been answered (not None and not empty)
    all_answered = all(val is not None and val != "" for val in question_values)
    is_disabled = not all_answered

    if all_answered:
        responses_dict = {f'sq{i+1}': value for i, value in enumerate(question_values)}
        if db.allows_respondent_to_continue(responses_dict):
            next = hrefs['next']['/screening']
            href = f"{next}#top"
        else:
            href = "/fullquota#top"
    else:
        href = None

    return is_disabled, href


# Callback to handle screening button click - register responses and time
@callback(
    Output('screening-button', 'n_clicks'),
    Input('screening-button', 'n_clicks'),
    [State('user-store', 'data')] + [State(f'question-{i}', 'value') for i in range(1, 3 + 1)],
    prevent_initial_call=True
)
def handle_screening_click(n_clicks, user_data, *question_values):
    if n_clicks and user_data:
        # Build responses dictionary - simple sq1, sq2, sq3... format
        responses_dict = {f'sq{i+1}': value for i, value in enumerate(question_values)}
        
        # Register responses and time in database
        if db.allows_respondent_to_continue(responses_dict):
            db.register_screening_responses(user_data['id'], responses_dict)
            db.register_time(user_data['id'], 'screening-button', time.time())
    
    return n_clicks


# Question-specific callbacks

