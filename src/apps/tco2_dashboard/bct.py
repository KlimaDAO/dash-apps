from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_content_bct(bct_deposited, bct_redeemed, fig_deposited_over_time, fig_redeemed_over_time):
    content_bct = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("Toucan Protocol : Base Carbon Tonne Pool", className='page-title'))
                ]), width=12, style={'padding-top': '30px'})),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    html.H5("TCO2 tokens deposited", className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(bct_deposited["Quantity"].sum())), className="card-text")
                ]), width=4),
            dbc.Col(
                dbc.Card([
                    html.H5("TCO2 tokens redeemed", className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(bct_redeemed["Quantity"].sum())), className="card-text")
                ]), width=4),
            dbc.Col(
                dbc.Card([
                    html.H5("BCT tokens retired", className="card-title"),
                    dbc.CardBody("Coming soon", className="card-text")
                ]), width=4),
        ], style={'padding-top': '60px'}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("TCO2 tokens deposited over time",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_deposited_over_time))
                ], className="card-graph")
            ], width=4),
            dbc.Col([
                    dbc.Card([
                        html.H5("TCO2 tokens redeemed over time",
                                className="card-title"),
                        dbc.CardBody(dcc.Graph(figure=fig_redeemed_over_time))
                    ], className="card-graph")
                    ], width=4),
            dbc.Col([
                    dbc.Card([
                        html.H5("BCT tokens retired over time",
                                className="card-title"),
                        dbc.CardBody("Coming soon", className="card-text")
                    ], className="card-graph"),
                    ], width=4)
        ])
    ]
    return content_bct
