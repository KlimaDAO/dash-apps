from dash import html, dash_table
from dash import dcc
import dash_bootstrap_components as dbc

from .constants import GRAY, DARK_GRAY


def create_pool_content(pool_ticker, pool_name, deposited, redeemed, retired, detail_df, fig_deposited_over_time,
                        fig_redeemed_over_time, fig_retired_over_time, fig_total_vintage, fig_total_map,
                        fig_total_metho, fig_total_project, retire_note, bridge_name="Toucan",
                        bridge_ticker="TCO2"):

    detail_df = detail_df[[
        'Project ID', 'Token Address', 'View on PolygonScan', 'Quantity', 'Vintage', 'Country', 'Project Type',
        'Methodology', 'Name',
    ]]

    if retired is None:
        retired_card = dbc.Card([
            html.H5(
                f"Cumulative Tonnes of {bridge_ticker} Retired from {pool_ticker}", className="card-title"),
            dbc.CardBody("Coming soon", className="card-text"),
        ], className="card-pool-summary")
        retired_graph = dbc.Card([
            html.H5(f"Cumulative Tonnes Retired from {pool_ticker} Over Time",
                    className="card-title"),
            dbc.CardBody("Coming soon", className="card-text"),
        ], className="card-graph")
    else:
        retired_card = dbc.Card([
            html.H5(
                f"Cumulative Tonnes of {bridge_ticker} Retired from {pool_ticker}", className="card-title"),
            dbc.CardBody("{:,}".format(
                int(retired["Quantity"].sum())), className="card-text"),
            dbc.CardFooter(retire_note, id="klima_retire_note")
        ], className="card-pool-summary")

        retired_graph = dbc.Card([
            html.H5(f"Cumulative Tonnes Retired from {pool_ticker} Over Time",
                    className="card-title"),
            dbc.CardBody(dcc.Graph(figure=fig_retired_over_time)),
            dbc.CardFooter(retire_note, id="klima_retire_note")
        ], className="card-graph")

    if redeemed["Quantity"].sum() == 0 or redeemed.empty:
        redeemed_graph = dbc.Card([
            html.H5(f"Cumulative Tonnes of {bridge_ticker} Redeemed Over Time",
                    className="card-title"),
            dbc.CardBody("0",
                         className="card-text"),
        ], className="card-graph")
    else:
        redeemed_graph = dbc.Card([
            html.H5(f"Cumulative Tonnes of {bridge_ticker} Redeemed Over Time",
                    className="card-title"),
            dbc.CardBody(dcc.Graph(figure=fig_redeemed_over_time))
        ], className="card-graph")

    def table_type(df_column):
        if [df_column] in [
                'Vintage', 'Quantity']:
            return 'numeric'
        else:
            return 'text'

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
                    html.H5(
                        f"Cumulative Tonnes of {bridge_ticker} Deposited", className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(deposited["Quantity"].sum())), className="card-text")
                ], className="card-pool-summary"), lg=4, md=12),
            dbc.Col(
                dbc.Card([
                    html.H5(
                        f"Cumulative Tonnes of {bridge_ticker} Redeemed", className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(redeemed["Quantity"].sum())), className="card-text")
                ], className="card-pool-summary"), lg=4, md=12),
            dbc.Col(retired_card, lg=4, md=12),
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
                    redeemed_graph
                    ], lg=4, md=12),
            dbc.Col([
                    retired_graph
                    ], lg=4, md=12)
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                dbc.CardBody(html.H2(f'Deep Dive into {pool_ticker}'),
                             style={'textAlign': 'center'})
            ]), lg=6, md=12),
            dbc.Col(),
        ], style={'paddingTop': '60px'}),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Vintage Start Dates",
                        className="card-title"),
                dcc.Graph(figure=fig_total_vintage)
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Origin of Tokenized Credits",
                        className="card-title"),
                dcc.Graph(figure=fig_total_map)
            ]), width=12),
            dbc.Col(),
        ]),
        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Methodologies",
                        className="card-title"),
                dcc.Graph(figure=fig_total_metho)
            ]), width=12),
            dbc.Col(),
        ]),
        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Projects", className="card-title"),
                dcc.Graph(figure=fig_total_project)
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5(f'{pool_ticker} Pool Composition Details',
                            className="card-title"),
                    dash_table.DataTable(
                        detail_df.to_dict('records'),
                        [{"name": i, "id": i, "presentation": "markdown", 'type': table_type(i)}
                            for i in detail_df.columns],
                        id='tbl',
                        style_header={
                            'backgroundColor': GRAY,
                            'text-align': 'center'
                        },
                        style_data={
                            'backgroundColor': DARK_GRAY,
                            'color': 'white'
                        },
                        style_data_conditional=[
                            {"if": {'column_id': 'Project ID'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {'column_id': 'Country'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {'column_id': 'Quantity'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {'column_id': 'Vintage'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {'column_id': 'Methodology'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {"state": "active"},
                             "backgroundColor": "#202020",
                             "border": "1px solid #2a2a2a",
                             "color": "white",
                             },
                        ],
                        style_table={'overflowX': 'auto'},
                        page_size=20,
                        sort_action='native',
                        filter_action='native',
                        style_filter={
                            'backgroundColor': GRAY,
                        }
                    ),
                ])
            ])
        ])
    ]
    return content
