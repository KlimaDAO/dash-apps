from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from .services import Metrics

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
    fig_total_carbon_supply_pie_chart
):
    polygon_metrics = Metrics().polygon().resolve()
    polygon_now = Metrics().polygon().latest()
    polygon_ago = Metrics().polygon().days_ago(7)
    # Polygon Supply Info
    polygonCarbonSupply = polygon_now["carbonMetrics_totalCarbonSupply"]
    polygonCarbonSupply7daysAgo = polygon_ago["carbonMetrics_totalCarbonSupply"]

    polygonSupplyChangeRatio = float(
        (polygonCarbonSupply - polygonCarbonSupply7daysAgo) / polygonCarbonSupply
    )

    polygonKlimaRetired = polygon_now["carbonMetrics_totalKlimaRetirements"]
    polygonRetired = polygon_now["carbonMetrics_totalRetirements"]
    polygonKlimaRetiredRatio = polygonKlimaRetired / polygonRetired

    polygon_supply_figure = get_supply_breakdown_figure(
        polygon_carbon_tokens, polygon_metrics
    )
    polygon_retirement_figure = get_polygon_retirement_breakdown_figure(
        polygon_metrics
    )

    # Eth Supply Info
    eth_metrics = Metrics().eth().resolve()
    eth_now = Metrics().eth().latest()
    eth_ago = Metrics().eth().days_ago(7)
    ethCarbonSupply = eth_now["carbonMetrics_totalCarbonSupply"]
    ethCarbonSupply7daysAgo = eth_ago["carbonMetrics_totalCarbonSupply"]

    ethSupplyChangeRatio = float(
        (ethCarbonSupply - ethCarbonSupply7daysAgo) / ethCarbonSupply
    )

    ethRetired = eth_now["carbonMetrics_totalRetirements"]

    eth_supply_figure = get_supply_breakdown_figure(
        eth_carbon_tokens, eth_metrics
    )
    eth_retirement_figure = get_eth_retirement_breakdown_figure(eth_metrics)

    # Celo Supply Info
    celo_metrics = Metrics().celo().resolve()
    celo_now = Metrics().celo().latest()
    celo_ago = Metrics().celo().days_ago(7)
    celoCarbonSupply = celo_now["carbonMetrics_totalCarbonSupply"]
    celoCarbonSupply7daysAgo = celo_ago["carbonMetrics_totalCarbonSupply"]
    celoSupplyChangeRatio = float(
        (celoCarbonSupply - celoCarbonSupply7daysAgo) / celoCarbonSupply
    )

    celo_supply_figure = get_supply_breakdown_figure(
        celo_carbon_tokens, celo_metrics
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
                                "{:,}".format(int(polygonCarbonSupply)),
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
                                "{:,}".format(int(ethCarbonSupply)),
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
                                "{:,}".format(int(celoCarbonSupply)),
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
