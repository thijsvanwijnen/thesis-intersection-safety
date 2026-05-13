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
                                """## Thank You! 🎉

### Study Complete
Thank you for participating in our Home Preferences Study! Your responses will help us better understand consumer preferences and housing decisions.

### What's Next?
Your compensation will be processed within 2-3 business days.

### Questions?
If you have any questions about this research, please contact:
- Email: researcher@university.edu
- Phone: (555) 123-4567

### Share Your Experience
If you enjoyed participating in this study, feel free to share it with friends who might also be interested in research participation.

**Thank you again for your valuable contribution to our research!**
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
