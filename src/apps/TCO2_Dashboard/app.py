import dash_bootstrap_components as dbc
import dash
from dash import html, Input, Output, callback
from dash import dcc
from Figures import *
from content_Toucan import *
from content_BCT import *

app = dash.Dash(title="KLIMA Dashboards",suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": '#232B2B',
    "font-size": 40
}

CONTENT_STYLE = {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [   
        dbc.Col(html.Img(src='assets/KlimaDAO-Logo.png', width=300, height=300),width=12),
        html.H3("Dashboards",style={'text-align':'center'}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("TCO2", href="/", active="exact",className="pill-nav"),
                dbc.NavLink("BCT", href="/BCT", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@callback(
    Output(component_id='Last X Days', component_property='children'),
    Output(component_id='volume plot', component_property='figure'),
    Output(component_id='vintage plot', component_property='figure'),
    Output(component_id='map', component_property='figure'),
    Output(component_id="fig_total_metho", component_property='children'),
    Input(component_id='summary_type', component_property='value'),
    Input(component_id='bridged_or_retired', component_property='value')
)
def update_output_div(summary_type, TCO2_type):
    if summary_type == 'Last 7 Days Performance':
        if TCO2_type == 'Bridged':
            return "Last 7 Days Performance", fig_seven_day_volume, fig_seven_day_vintage, fig_seven_day_map, dcc.Graph(figure=fig_seven_day_metho)
        elif TCO2_type == 'Retired':
            return "Last 7 Days Performance", fig_seven_day_volume_retired, fig_seven_day_vintage_retired, fig_seven_day_map_retired, dcc.Graph(figure=fig_seven_day_metho_retired)

    elif summary_type == 'Last 30 Days Performance':
        if TCO2_type == 'Bridged':
            return "Last 30 Days Performance", fig_thirty_day_volume, fig_thirty_day_vintage, fig_thirty_day_map, dcc.Graph(figure=fig_thirty_day_metho)
        elif TCO2_type == 'Retired':
            return "Last 30 Days Performance", fig_thirty_day_volume_retired, fig_thirty_day_vintage_retired, fig_thirty_day_map_retired, dcc.Graph(figure=fig_thirty_day_metho_retired)

    elif summary_type == 'Overall Performance':
        if TCO2_type == 'Bridged':
            return "Overall Performance", fig_total_volume, fig_total_vintage, fig_total_map,\
                dcc.Graph(figure=fig_total_metho)
        elif TCO2_type == 'Retired':
            return "Overall Performance", fig_total_volume_retired, fig_total_vintage_retired, fig_total_map_retired, \
                dcc.Graph(figure=fig_total_metho_retired)


@callback(
    Output(component_id='eligible pie chart plot',
           component_property='figure'),
    Input(component_id='pie_chart_summary', component_property='value')
)
def update_eligible_pie_chart(pool_key):
    fig_eligible_pool_pie_chart = eligible_pool_pie_chart(df_carbon, pool_key)
    return fig_eligible_pool_pie_chart


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return content_Toucan

    elif pathname == "/BCT":
        return content_BCT

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# For Gunicorn to reference
server = app.server


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
