import dash
from dash_extensions.enrich import html
from src.apps.treasury.app import app

CONTENT_STYLE = {
    "position": "relative",
    "margin-right": "0rem",
    "margin-left": "0rem",
    "background-color": "#202020",
    "height": "100vh"
}
FOOTER_STYLE = {
    "position": "relative",
    "bottom": 0,
    "left": 0,
    "right": 0,
    "height": "6rem",
    "padding": "1rem 1rem",
    "background-color": "#202020",
}

app.layout = html.Div([
    html.Div([
        html.H1("KlimaDAO Treasury Dashboard")
    ], className='center_2'),
    dash.page_container
])

# For Gunicorn to reference
server = app.server


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
