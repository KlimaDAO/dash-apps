from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

from src.apps.tco2_dashboard.figures import (
    get_eth_retirement_breakdown_figure,
    get_polygon_retirement_breakdown_figure,
    get_supply_breakdown_figure,
)


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
    df_carbon_metrics_celo,
    fig_total_carbon_supply_pie_chart,
):
    # Polygon Supply Info
    polygonCarbonSupply = int(
        df_carbon_metrics_polygon["carbonMetrics_totalCarbonSupply"].iloc[0]
    )
    polygonCarbonSupply7daysAgo = int(
        df_carbon_metrics_polygon["carbonMetrics_totalCarbonSupply"].iloc[6]
    )

    polygonSupplyChangeRatio = float(
        (polygonCarbonSupply - polygonCarbonSupply7daysAgo) / polygonCarbonSupply
    )

    polygonKlimaRetired = float(
        df_carbon_metrics_polygon["carbonMetrics_totalKlimaRetirements"].iloc[0]
    )
    polygonRetired = float(
        df_carbon_metrics_polygon["carbonMetrics_totalRetirements"].iloc[0]
    )
    polygonKlimaRetiredRatio = polygonKlimaRetired / polygonRetired

    polygon_supply_figure = get_supply_breakdown_figure(
        polygon_carbon_tokens, df_carbon_metrics_polygon
    )
    polygon_retirement_figure = get_polygon_retirement_breakdown_figure(
        df_carbon_metrics_polygon
    )

    # Eth Supply Info
    ethCarbonSupply = int(
        df_carbon_metrics_eth["carbonMetrics_totalCarbonSupply"].iloc[0]
    )
    ethCarbonSupply7daysAgo = int(
        df_carbon_metrics_eth["carbonMetrics_totalCarbonSupply"].iloc[6]
    )

    ethSupplyChangeRatio = float(
        (ethCarbonSupply - ethCarbonSupply7daysAgo) / ethCarbonSupply
    )

    ethRetired = float(df_carbon_metrics_eth["carbonMetrics_totalRetirements"].iloc[0])

    eth_supply_figure = get_supply_breakdown_figure(
        eth_carbon_tokens, df_carbon_metrics_eth
    )
    eth_retirement_figure = get_eth_retirement_breakdown_figure(df_carbon_metrics_eth)

    # Celo Supply Info
    celoCarbonSupply = int(
        df_carbon_metrics_celo["carbonMetrics_totalCarbonSupply"].iloc[0]
    )
    celoCarbonSupply7daysAgo = int(
        df_carbon_metrics_celo["carbonMetrics_totalCarbonSupply"].iloc[6]
    )

    celoSupplyChangeRatio = float(
        (celoCarbonSupply - celoCarbonSupply7daysAgo) / celoCarbonSupply
    )

    celo_supply_figure = get_supply_breakdown_figure(
        celo_carbon_tokens, df_carbon_metrics_celo
    )

    content = [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                "Digital Carbon Supply",
                                className="page-title-carbon-supply",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center", "margin-bottom": "20px"},
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    "Breakdown of Total Digital Carbon Supply by Blockchain Platform",
                                    className="graph-label-carbon-supply",
                                ),
                                dbc.CardBody(
                                    dcc.Graph(figure=fig_total_carbon_supply_pie_chart)
                                ),
                            ]
                        )
                    ],
                    width=12,
                ),
            ],
            style={"textAlign": "center", "margin-bottom": "20px"},
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                "Polygon Digital Carbon",
                                className="page-title-carbon-supply",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center", "margin-bottom": "20px"},
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Total Supply (Tonnes)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:,}".format(polygonCarbonSupply),
                                className="card-text-carbon-supply",
                            ),
                            html.H5(
                                "Supply Change (last 7 days)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(polygonSupplyChangeRatio),
                                className="card-text-carbon-supply",
                            ),
                        ]
                    ),
                    lg=6,
                    md=12,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Total Retirements (Tonnes)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:,}".format(int(polygonRetired)),
                                className="card-text-carbon-supply",
                            ),
                            html.H5(
                                "Percentage Retired via KlimaDAO",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(polygonKlimaRetiredRatio),
                                className="card-text-carbon-supply",
                            ),
                        ]
                    ),
                    lg=6,
                    md=12,
                ),
            ],
            style={"margin-bottom": "20px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    "Supply", className="graph-label-carbon-supply"
                                ),
                                dbc.CardBody(dcc.Graph(figure=polygon_supply_figure)),
                            ]
                        )
                    ],
                    lg=6,
                    md=12,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    "Retirements", className="graph-label-carbon-supply"
                                ),
                                dbc.CardBody(
                                    dcc.Graph(figure=polygon_retirement_figure)
                                ),
                            ]
                        )
                    ],
                    lg=6,
                    md=12,
                ),
            ],
            style={"margin-bottom": "40px"},
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                "Ethereum Digital Carbon",
                                className="page-title-carbon-supply",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center", "margin-bottom": "20px"},
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Total Supply (Tonnes)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:,}".format(ethCarbonSupply),
                                className="card-text-carbon-supply",
                            ),
                            html.H5(
                                "Supply Change (last 7 days)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(ethSupplyChangeRatio),
                                className="card-text-carbon-supply",
                            ),
                        ]
                    ),
                    lg=6,
                    md=12,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Total Retirements (Tonnes)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:,}".format(int(ethRetired)),
                                className="card-text-carbon-supply",
                            ),
                            html.H5(
                                "Percentage Retired by Klima",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(0), className="card-text-carbon-supply"
                            ),
                        ]
                    ),
                    lg=6,
                    md=12,
                ),
            ],
            style={"margin-bottom": "20px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    "Supply", className="graph-label-carbon-supply"
                                ),
                                dbc.CardBody(dcc.Graph(figure=eth_supply_figure)),
                            ]
                        )
                    ],
                    lg=6,
                    md=12,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    "Retirements", className="graph-label-carbon-supply"
                                ),
                                dbc.CardBody(dcc.Graph(figure=eth_retirement_figure)),
                            ]
                        )
                    ],
                    lg=6,
                    md=12,
                ),
            ],
            style={"margin-bottom": "40px"},
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                "Celo Digital Carbon",
                                className="page-title-carbon-supply",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center", "margin-bottom": "20px"},
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Total Supply (Tonnes)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:,}".format(celoCarbonSupply),
                                className="card-text-carbon-supply",
                            ),
                            html.H5(
                                "Supply Change (last 7 days)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(celoSupplyChangeRatio),
                                className="card-text-carbon-supply",
                            ),
                        ]
                    ),
                    lg=6,
                    md=12,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Total Retirements (Tonnes)",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:,}".format(0), className="card-text-carbon-supply"
                            ),
                            html.H5(
                                "Percentage Retired via KlimaDAO",
                                className="card-title-carbon-supply",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(0), className="card-text-carbon-supply"
                            ),
                        ]
                    ),
                    lg=6,
                    md=12,
                ),
            ],
            style={"margin-bottom": "20px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    "Supply", className="graph-label-carbon-supply"
                                ),
                                dbc.CardBody(dcc.Graph(figure=celo_supply_figure)),
                            ]
                        )
                    ],
                    lg=6,
                    md=12,
                ),
            ]
        ),
    ]
    return content
