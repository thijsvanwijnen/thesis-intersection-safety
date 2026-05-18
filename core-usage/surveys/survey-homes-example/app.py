import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from dash import get_relative_path as asset

# Dash survey app and server
app = dash.Dash(__name__, 
				external_stylesheets = [dbc.themes.BOOTSTRAP], 
				use_pages = True,
				suppress_callback_exceptions = True)
server = app.server
survey_color = "#2E8B57"

def header():
    left_logo = html.Img(src = asset("/assets/logos/user_logo.png"), className = "my-3", style = {"height": "60px"})
    right_logo = html.Img(src = asset("/assets/logos/pixelsurvey_logo.png"), className = "my-3", style = {"height": "60px"})
    title = html.H1("House Preferences Study", style = {"fontSize": "30px", "color":"white"})
    subtitle = html.H6("A comprehensive study on housing choices and residential preferences", style = {"fontSize": "20px", "color":"white"}, className = "lead")

    return html.Div(
        children = [ 
            dbc.Row( 
                children  = [
                    dbc.Col(left_logo, width = 2, align = "center", style = {"textAlign": "left", "marginLeft": "2%"}),
                    dbc.Col([title, subtitle], align="center", style = {"textAlign": "center"}),
                    dbc.Col(right_logo, width = 2, align="center", style = {"textAlign": "right", "marginRight": "2%"})],
            )],
        className = "py-1", style = {"backgroundColor": survey_color})


def footer():
    return html.Div([
        html.Hr(style={"margin": "0.5rem 0", "border": "1px solid #e0e0e0"}),
        html.Div([
            html.P([
                "Survey ID: ",
                html.Strong("homes-example", style={"color": survey_color}),
                " | Generated with ",
                html.Strong("PixelSurvey (Albatros) 1.0", style={"color": survey_color}),
            ], style={"margin": "0.3rem 0", "fontSize": "14px", "color": "#666"}),
            html.P([
                "PixelSurvey® is a registered trademark © 2025. All rights reserved."
            ], style={"margin": "0.3rem 0", "fontSize": "12px", "color": "#888"}),
        ], style={"textAlign": "center", "padding": "0.5rem 0"})
    ])


app.layout = html.Div([
    # Global top anchor for all pages
    html.Div(id="top", style={"position": "absolute", "top": "0"}),
    dcc.Store(id = "user-store", data = {"id": -1, "tasks": None}, storage_type = "session"),
    dcc.Store(id = "hrefs-store", data = {"next": None}, storage_type = "session"),
	dcc.Store(id = "external-user", data = {"id": -1}, storage_type = "session"),
    dcc.Store(id = "last_task_resp_act1", data = {"task": None}, storage_type = "session"),
    dcc.Location(id = "url", refresh = False),
    header(),
    dash.page_container,
    html.Hr(),
    footer()
])


if __name__ == "__main__":
	app.run(debug = True)