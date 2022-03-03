from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_content_bct(bct_deposited, bct_redeemed, fig_deposited_over_time, fig_redeemed_over_time):
    content_bct = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("Toucan Carbon Pool: Base Carbon Tonne (BCT)", className='page-title'))
                ]), width=12, style={'textAlign': 'center'})),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    html.H5("Cumulative Tonnes of TCO2 Deposited", className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(bct_deposited["Quantity"].sum())), className="card-text")
                ]), width=4),
            dbc.Col(
                dbc.Card([
                    html.H5("Tonnes of TCO2 Redeemed", className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(bct_redeemed["Quantity"].sum())), className="card-text")
                ]), width=4),
            dbc.Col(
                dbc.Card([
                    html.H5("Tonnes of TCO2 Retired from BCT", className="card-title"),
                    dbc.CardBody("Coming soon", className="card-text")
                ]), width=4),
        ], style={'paddingTop': '60px'}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Cumulative Tonnes of TCO2 Deposited Over Time",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_deposited_over_time))
                ], className="card-graph")
            ], width=4),
            dbc.Col([
                    dbc.Card([
                        html.H5("Cumulative Tonnes of TCO2 Redeemed Over Time",
                                className="card-title"),
                        dbc.CardBody(dcc.Graph(figure=fig_redeemed_over_time))
                    ], className="card-graph")
                    ], width=4),
            dbc.Col([
                    dbc.Card([
                        html.H5("Tonnes Retired from BCT Over Time",
                                className="card-title"),
                        dbc.CardBody("Coming soon", className="card-text")
                    ], className="card-graph"),
                    ], width=4)
        ])
    ]
    return content_bct
