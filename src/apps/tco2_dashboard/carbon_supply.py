from dash import html, dash_table
from dash import dcc
import dash_bootstrap_components as dbc

from src.apps.tco2_dashboard.figures import get_eth_retirement_breakdown_figure, \
    get_polygon_retirement_breakdown_figure, get_supply_breakdown_figure


bct_token = {"name": "bct", "color": "#eff542"}
nct_token = {"name": "nct", "color": "#6fa8dc"}
mco2_token = {"name": "mco2", "color": "#93c47d"}
ubo_token = {"name": "ubo", "color": "#c27ba0"}
nbo_token = {"name": "nbo", "color": "#8e7cc3"}


polygon_carbon_tokens = [
    bct_token,
    nct_token,
    mco2_token,
    ubo_token,
    nbo_token,
]

eth_carbon_tokens = [
    mco2_token,
]

celo_carbon_tokens = [
    bct_token,
    nct_token,
    mco2_token,
]


def create_carbon_supply_content(
    df_carbon_metrics_polygon,
    df_carbon_metrics_eth,
    df_carbon_metrics_celo
):
    # Polygon Supply Info
    polygonCarbonSupply = int(df_carbon_metrics_polygon["carbonMetrics_totalCarbonSupply"].iloc[0])
    polygonCarbonSupply7daysAgo = int(df_carbon_metrics_polygon["carbonMetrics_totalCarbonSupply"].iloc[6])

    polygonSupplyChangeRatio = float((polygonCarbonSupply - polygonCarbonSupply7daysAgo) / polygonCarbonSupply)

    polygonKlimaRetired = float(df_carbon_metrics_polygon["carbonMetrics_totalKlimaRetirements"].iloc[0])
    polygonRetired = float(df_carbon_metrics_polygon["carbonMetrics_totalRetirements"].iloc[0])
    polygonKlimaRetiredRatio = polygonKlimaRetired / polygonRetired

    polygon_supply_figure = get_supply_breakdown_figure(polygon_carbon_tokens, df_carbon_metrics_polygon)
    polygon_retirement_figure = get_polygon_retirement_breakdown_figure(df_carbon_metrics_polygon)

    # Eth Supply Info
    ethCarbonSupply = int(df_carbon_metrics_eth["carbonMetrics_totalCarbonSupply"].iloc[0])
    ethCarbonSupply7daysAgo = int(df_carbon_metrics_eth["carbonMetrics_totalCarbonSupply"].iloc[6])

    ethSupplyChangeRatio = float((ethCarbonSupply - ethCarbonSupply7daysAgo) / ethCarbonSupply)

    ethRetired = float(df_carbon_metrics_eth["carbonMetrics_totalRetirements"].iloc[0])

    eth_supply_figure = get_supply_breakdown_figure(eth_carbon_tokens, df_carbon_metrics_eth)
    eth_retirement_figure = get_eth_retirement_breakdown_figure(df_carbon_metrics_eth)

    # Celo Supply Info
    celoCarbonSupply = int(df_carbon_metrics_celo["carbonMetrics_totalCarbonSupply"].iloc[0])
    celoCarbonSupply7daysAgo = int(df_carbon_metrics_celo["carbonMetrics_totalCarbonSupply"].iloc[6])

    celoSupplyChangeRatio = float((celoCarbonSupply - celoCarbonSupply7daysAgo) / celoCarbonSupply)

    celo_supply_figure = get_supply_breakdown_figure(celo_carbon_tokens, df_carbon_metrics_celo)

    content = [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                "Polygon On Chain Carbon",
                                className="page-title",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center"},
            )
        ),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    html.H5("Total Supply In Tonnes",
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        polygonCarbonSupply),
                        className="card-text"),
                    html.H5("Supply change in the last 7d",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        polygonSupplyChangeRatio),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=6),
            dbc.Col(
                dbc.Card([
                    html.H5("Total Retirements In Tonnes",
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(polygonRetired)),
                        className="card-text"),
                    html.H5("Percentage Retired By Klima",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        polygonKlimaRetiredRatio),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=6),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Supply",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=polygon_supply_figure))
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    html.H5("Retirements",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=polygon_retirement_figure))
                ])
            ], width=6),
        ]),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                "Ethereum On Chain Carbon",
                                className="page-title",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center"},
            )
        ),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    html.H5("Total Supply In Tonnes",
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        ethCarbonSupply),
                        className="card-text"),
                    html.H5("Supply change in the last 7d",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        ethSupplyChangeRatio),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=6),
            dbc.Col(
                dbc.Card([
                    html.H5("Total Retirements In Tonnes",
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(ethRetired)),
                        className="card-text"),
                    html.H5("Percentage Retired By Klima",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        0),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=6),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Supply",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=eth_supply_figure))
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    html.H5("Retirements",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=eth_retirement_figure))
                ])
            ], width=6),
        ]),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                "Celo On Chain Carbon",
                                className="page-title",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center"},
            )
        ),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    html.H5("Total Supply In Tonnes",
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        celoCarbonSupply),
                        className="card-text"),
                    html.H5("Supply change in the last 7d",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        celoSupplyChangeRatio),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=6),
            dbc.Col(
                dbc.Card([
                    html.H5("Total Retirements In Tonnes",
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        0),
                        className="card-text"),
                    html.H5("Percentage Retired By Klima",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        0),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=6),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Supply",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=celo_supply_figure))
                ])
            ], width=6),
        ]),
    ]
    return content
