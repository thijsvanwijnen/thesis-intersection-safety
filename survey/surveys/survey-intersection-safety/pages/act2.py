import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import time
from database import Database

# Database
db = Database('database.db')

# Register this page
dash.register_page(__name__, path="/act2", name='Questionnaire')

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
                            value=99,
                            label="99%",
                            style={"height": "15px", "fontSize": "10px"},
                            color="primary"
                        )
                    ], style={"marginBottom": "2rem", "marginTop": "0.5rem"}),

                    # Instructions card
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Markdown(
                                """## Achtergrondvragen

Tot slot enkele vragen over uw professionele achtergrond.
Deze informatie wordt gebruikt om het expertpanel te karakteriseren en wordt niet
gekoppeld aan uw individuele vergelijkingsantwoorden.
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
                    
                    # List of Questionnaire questions
                    html.Div([
                        dbc.Card([
    dbc.CardBody([
        # Question text
        dbc.Row([
            dbc.Col([
                dbc.Label(
                    "Hoe vaak voert u locatie-inspecties of veiligheidsaudits uit bij kruispunten? *",
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
                        
                        {"label": "Wekelijks of vaker", "value": "1"},
                        
                        {"label": "Maandelijks", "value": "2"},
                        
                        {"label": "Een paar keer per jaar", "value": "3"},
                        
                        {"label": "Zelden", "value": "4"}
                        
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
                    "Hoe bekend bent u met de ontwerpprincipes van Duurzaam Veilig? *",
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
                        
                        {"label": "Zeer bekend — ik pas ze regelmatig toe", "value": "1"},
                        
                        {"label": "Bekend — ik ken de hoofdprincipes", "value": "2"},
                        
                        {"label": "Enigszins bekend", "value": "3"},
                        
                        {"label": "Niet bekend", "value": "4"}
                        
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
                    "Heeft u opmerkingen over de beoordelingstaak of de kruispuntfoto's die u aan de onderzoeker wilt doorgeven? (optioneel)",
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
        
        # Answer textarea
        dbc.Row([
            dbc.Col([
                dbc.Textarea(
                    id="question-3",
                    placeholder="Please type your response here...",
                    style={
                        "fontSize": "14px",
                        "minHeight": "100px"
                    },
                    required=False
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
                            id="act2-button",
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


# Callback to enable/disable continue button based on all questionnaire questions being answered
@callback(
    [Output('act2-button', 'disabled'),
     Output('act2-button', 'href')],
     State('hrefs-store', 'data'),
    [Input(f'question-{i}', 'value') for i in range(1, 3 + 1)],
    prevent_initial_call=True
)
def toggle_continue_button(hrefs, *question_values):
    # Check if all questions have been answered (not None and not empty)
    all_answered = all(val is not None and val != "" for val in question_values)
    is_disabled = not all_answered
    next = hrefs['next']['/act2']
    href = f"{next}#top" if all_answered else None
    return is_disabled, href


# Callback to handle questionnaire button click - register responses and time
@callback(
    Output('act2-button', 'n_clicks'),
    Input('act2-button', 'n_clicks'),
    [State('hrefs-store', 'data'),
     State('user-store', 'data')] + [State(f'question-{i}', 'value') for i in range(1, 3 + 1)],
    prevent_initial_call=True
)
def handle_questionnaire_click(n_clicks, hrefs, user_data, *question_values):
    if n_clicks and user_data:
        responses_dict = {f'act2_q{i+1}': value for i, value in enumerate(question_values)}
        
        # Register responses and time in database
        db.register_questionnaire_responses(user_data['id'], 'act2', responses_dict)
        db.register_time(user_data['id'], 'act2-button', time.time())

        if hrefs['next']['/act2'] == '/end':
            db.update_quota(user_data['id'])
    
    return n_clicks


# Question-specific callbacks

