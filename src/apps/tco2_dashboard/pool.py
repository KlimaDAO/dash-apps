from dash import html, dash_table
from dash import dcc
import dash_bootstrap_components as dbc

from .constants import GRAY, DARK_GRAY


def create_pool_content(pool_ticker, pool_name, deposited, redeemed, detail_df, fig_deposited_over_time,
                        fig_redeemed_over_time, bridge_name="Toucan", bridge_ticker="TCO2"):
    content = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1(f"{bridge_name} Carbon Pool: {pool_name} ({pool_ticker})", className='page-title'))
                ]), width=12, style={'textAlign': 'center'})),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    html.H5(f"Cumulative Tonnes of {bridge_ticker} Deposited", className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(deposited["Quantity"].sum())), className="card-text")
                ]), lg=4, md=12),
            dbc.Col(
                dbc.Card([
                    html.H5(f"Cumulative Tonnes of {bridge_ticker} Redeemed", className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(redeemed["Quantity"].sum())), className="card-text")
                ]), lg=4, md=12),
            dbc.Col(
                dbc.Card([
                    html.H5(f"Tonnes of {bridge_ticker} Retired from {pool_ticker}", className="card-title"),
                    dbc.CardBody("Coming soon", className="card-text")
                ]), lg=4, md=12),
        ], style={'paddingTop': '60px'}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5(f"Cumulative Tonnes of {bridge_ticker} Deposited Over Time",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_deposited_over_time))
                ], className="card-graph")
            ], lg=4, md=12),
            dbc.Col([
                    dbc.Card([
                        html.H5(f"Cumulative Tonnes of {bridge_ticker} Redeemed Over Time",
                                className="card-title"),
                        dbc.CardBody(dcc.Graph(figure=fig_redeemed_over_time))
                    ], className="card-graph")
                    ], lg=4, md=12),
            dbc.Col([
                    dbc.Card([
                        html.H5(f"Tonnes Retired from {pool_ticker} Over Time",
                                className="card-title"),
                        dbc.CardBody("Coming soon", className="card-text")
                    ], className="card-graph"),
                    ], lg=4, md=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5(f'{pool_ticker} Pool Composition Details', className="card-title"),
                    dash_table.DataTable(
                        detail_df.to_dict('records'),
                        [{"name": i, "id": i, "presentation": "markdown"} for i in detail_df.columns],
                        id='tbl',
                        style_header={
                            'backgroundColor': GRAY,
                            'text-align': 'center'
                        },
                        style_data={
                            'backgroundColor': DARK_GRAY
                        },
                        style_table={'overflowX': 'auto'},
                        page_size=20,
                        sort_action='native'
                    ),
                ])
            ])
        ])
    ]
    return content
