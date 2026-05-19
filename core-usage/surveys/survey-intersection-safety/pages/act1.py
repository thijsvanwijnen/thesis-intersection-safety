import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import time
from database import Database


# Database
db = Database('database.db')


# Register this page with dynamic path template
dash.register_page(__name__, path_template="/act1/<task_number>", name='1_stated_choice')


# Task content generator



def task_content_generator(data):
    """Generate stated choice content for current task"""
    
    # Unpack the task data
    alt1_att1_straatbeeld_url, alt1_att2_verkeersintensiteit, alt2_att1_straatbeeld_url, alt2_att2_verkeersintensiteit = data
    
    # Generate the alternative cards
    card_alternative_1 = dbc.Card(
            id="act1-alternative-1",
            children=[
                dbc.CardHeader(
                    html.H4(f"Kruispunt #1", className="card-title")
                )
                
                
                ,
                dbc.CardImg(src=f"{alt1_att1_straatbeeld_url}", top=True)
                
                
                ,
                dbc.CardBody(
                    dbc.Row(children=[
                        
                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(
                                    "Verkeersintensiteit", 
                                    style={"fontSize": "15px"}
                                ),
                                dbc.CardBody(
                                    dcc.Markdown(f"**{alt1_att2_verkeersintensiteit}** aantal voertuigen per dag"), 
                                    style={"fontSize": "20px"}
                                )
                            ])
                        )
                        
                    ])
                )
                
            ],
            style={"width": "36rem"}
        )
    
    card_alternative_2 = dbc.Card(
            id="act1-alternative-2",
            children=[
                dbc.CardHeader(
                    html.H4(f"Kruispunt #2", className="card-title")
                )
                
                
                ,
                dbc.CardImg(src=f"{alt2_att1_straatbeeld_url}", top=True)
                
                
                ,
                dbc.CardBody(
                    dbc.Row(children=[
                        
                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(
                                    "Verkeersintensiteit", 
                                    style={"fontSize": "15px"}
                                ),
                                dbc.CardBody(
                                    dcc.Markdown(f"**{alt2_att2_verkeersintensiteit}** aantal voertuigen per dag"), 
                                    style={"fontSize": "20px"}
                                )
                            ])
                        )
                        
                    ])
                )
                
            ],
            style={"width": "36rem"}
        )
    
    # Return the main experiment card
    return lambda current_task: dbc.Card([
        dbc.CardBody([
            # Question text with circular task indicator
            dbc.Row([
                dbc.Col([
                    html.Div([
                        # Circular task number
                        html.Div(
                            f"Task {current_task}",
                            style={
                                "backgroundColor": "#007bff",
                                "color": "white",
                                "borderRadius": "20px",
                                "minWidth": "60px",
                                "height": "40px",
                                "padding": "0 12px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "bold",
                                "fontSize": "14px",
                                "marginRight": "15px",
                                "whiteSpace": "nowrap"
                            }
                        ),
                        # Question text
                        html.Span(
                            "Bij welk kruispunt is de kans op een ernstig verkeersongeval op de rijbaan (letsel of dodelijk) hoger?",
                            style={
                                "fontWeight": "bold",
                                "color": "darkblue",
                                "fontSize": "22px",
                                "lineHeight": "40px"
                            }
                        )
                    ], style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "marginBottom": "2rem"
                    })
                ])
            ]),
            
            # RadioItems with alternative cards
            html.Div([
                dbc.RadioItems(
                    id="stated-choice-1-response",
                    inline=True,
                    input_style={"borderColor": "#000000"},
                    options=[
                        {"label": card_alternative_1, "value": 1},
                        {"label": card_alternative_2, "value": 2}
                    ]
                )
            ], style={
                "textAlign": "center",
                "marginBottom": "2rem"
            })
        ], style={"padding": "1.5rem"})
    ], style={
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "borderRadius": "8px", 
        "border": "none",
        "marginBottom": "1.5rem"
    })



# Page layout
def layout(task_number=None):
    if task_number is None:
        task_number = "1"
    
    current_task = int(task_number)
    n_act_tasks = 36
    n_prev_tasks = 0
    n_total_tasks = 37

    progress = ((n_prev_tasks+current_task)/n_total_tasks) * 100
    if progress == 100:
        progress == 99
    progress_label = int(round(progress,0))
    
    return html.Div([
        
        # Main content container - centered and 80% width
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Progress indicator
                    html.Div([
                        dbc.Progress(
                            value= progress,
                            label=f"{progress_label}%",
                            style={"height": "15px", "fontSize": "10px"},
                            color="primary"
                        )
                    ], style={"marginBottom": "2rem", "marginTop": "0.5rem"}),
                    
                    # Instructions card
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Markdown(
                                """## Paarsgewijze veiligheidsvergelijking
Baseer uw oordeel op het zichtbare ontwerp.
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
                    
                    # Dynamic experiment content
                    html.Div(None, id="task-content-act1", style={"marginBottom": "2rem"}),

                    # Navigation buttons
                    html.Div([
                        dbc.Button(
                            "Continue",
                            id="act1-button",
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


## Callback to load experiment content based on current task
@callback(
    Output('task-content-act1', 'children'),
    [
        Input('url', 'pathname'),
        State('user-store', 'data')
    ],
)
def load_task_content(pathname, user_data):
    act_key = 'act1'
    task_nr = pathname.split('/')[-1]
    if pathname.split('/')[-2] == 'act1':
        task_data = user_data['tasks'][f'{act_key}_task_{task_nr}']
        return task_content_generator(task_data)(int(task_nr))
    else:
        return None


## Callback to change visually the selection

@callback(
    Output("act1-alternative-1", "color"),
    Output("act1-alternative-2", "color"),
    Output("last_task_resp_act1", "data"),
    State("url", "pathname"),
    State("last_task_resp_act1", "data"),
    Input("stated-choice-1-response", "value"),
    prevent_initial_call=True
)
def selection_made(pathname, last_task, selection):
    color = "#a3ebff"
    task_nr = pathname.split('/')[-1]
    if selection is None:
        return None, None, last_task
    elif selection == 1:
        return color, None, {"task": task_nr}
    elif selection == 2:
        return None, color, {"task": task_nr}



## Callback to enable/disable continue button based on all screening questions being answered

@callback(
    [Output('act1-button', 'disabled'),
     Output('act1-button', 'href')],
     State('hrefs-store', 'data'),
     State('url', 'pathname'),
    [Input('stated-choice-1-response', 'value')],
    prevent_initial_call=True
)
def toggle_continue_button(hrefs, pathname, selection):
    # Check if all questions have been answered (not None and not empty)
    is_disabled = selection is None
    next = hrefs["next"][pathname]
    href = f"{next}#top" if not is_disabled else None
    return is_disabled, href



## Callback to handle act button click - register response and time

@callback(
    Output('act1-button', 'n_clicks'),
    Input('act1-button', 'n_clicks'),
    State('hrefs-store', 'data'),
    State('user-store', 'data'),
    State("last_task_resp_act1", "data"),
    State('stated-choice-1-response', 'value'),
    prevent_initial_call=True
)
def handle_screening_click(n_clicks, hrefs, user_data, last_task, response):
    if n_clicks and user_data:
        # Register responses and time in database
        task_nr = last_task["task"]
        db.register_experiment_response(user_data['id'], 'act1', int(task_nr), response)
        db.register_time(user_data['id'], f'act1-task-{task_nr}-button', time.time())

        # If this was the last act1 task (next page is not another act1 task),
        # mark the task set as finished. update_quota is handled in act2.py.
        next_href = hrefs['next'][f'/act1/{task_nr}']
        if not next_href.startswith('/act1/'):
            db.mark_set_finished(user_data['id'])
    return n_clicks
