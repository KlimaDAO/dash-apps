from functools import reduce
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from .constants import BETWEEN_SECTION_STYLE
from .services import Offsets


def create_offchain_vs_onchain_content(
    fig_bridges_pie_chart,
):

    def total_quantity(bridges, status):
        return reduce(
            lambda acc, bridge: acc + Offsets().filter(bridge, None, status).sum("Quantity"),
            bridges,
            0)

    header = dbc.Row(
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(html.H1("State of Digital Carbon")),
                ]
            ),
            width=12,
            style={"textAlign": "center"},
        ),
    )

    sum_total_tokenized = total_quantity(["Toucan", "Moss", "C3"], "bridged")
    sum_total_onchain_retired = total_quantity(["Toucan", "Moss", "C3"], "retired")
    sum_offchain = Offsets().filter("offchain", None, "issued").sum("Quantity")
    sum_offchain_retired = Offsets().filter("offchain", None, "retired").sum("Quantity")

    offchain_retired_card = dbc.Col(
        [
            dbc.Card(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "Off-Chain Verra Registry Credits Retired",
                                    className="card-title",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(
                                        int(sum_offchain_retired)
                                    ),
                                    className="card-text-continuation",
                                ),
                            ],
                            style={"margin": "0px", "padding": "0px"},
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "Percentage of Retired Credits",
                                    className="card-title",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(
                                        sum_offchain_retired
                                        / (
                                            sum_offchain
                                            - sum_total_tokenized
                                        )
                                    ),
                                    className="card-text",
                                ),
                            ],
                            style={"margin": "0px", "padding": "0px"},
                        ),
                        width=12,
                    ),
                ]
            )
        ],
        lg=6,
        md=12,
    )

    onchain_retired_card = dbc.Col(
        [
            dbc.Card(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "On-Chain Verra Registry Credits Retired",
                                    className="card-title",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(sum_total_onchain_retired)),
                                    className="card-text-continuation",
                                ),
                            ],
                            style={"margin": "0px", "padding": "0px"},
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "Percentage of Retired Credits",
                                    className="card-title",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(
                                        sum_total_onchain_retired / sum_total_tokenized
                                    ),
                                    className="card-text",
                                ),
                            ],
                            style={"margin": "0px", "padding": "0px"},
                        ),
                        width=12,
                    ),
                ]
            )
        ],
        lg=6,
        md=12,
    )

    content = [
        header,
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Verra Registry Credits Issued", className="card-title"
                            ),
                            dbc.CardBody(
                                "{:,}".format(int(sum_offchain)),
                                className="card-text",
                            ),
                        ]
                    ),
                    lg=4,
                    md=12,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Verra Registry Credits Tokenized",
                                className="card-title",
                            ),
                            dbc.CardBody(
                                "{:,}".format(int(sum_total_tokenized)),
                                className="card-text",
                            ),
                        ]
                    ),
                    lg=4,
                    md=12,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "Percentage of Tokenized Credits",
                                className="card-title",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(
                                    (sum_total_tokenized / sum_offchain)
                                ),
                                className="card-text",
                            ),
                        ]
                    ),
                    lg=4,
                    md=12,
                ),
            ],
            style=BETWEEN_SECTION_STYLE,
        ),
        dbc.Row([offchain_retired_card, onchain_retired_card]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    "Breakdown of Tokenized Credits by Bridges",
                                    className="card-title",
                                ),
                                dbc.CardBody(dcc.Graph(figure=fig_bridges_pie_chart)),
                            ]
                        )
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H2(
                                        "Deep Dive into Off-Chain vs On-Chain Carbon Credits"
                                    )
                                ),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader(
                                                                    html.H5(
                                                                        "Issued or Retired Credits?",
                                                                        className="card-title",
                                                                    ),
                                                                ),
                                                                dbc.CardBody(
                                                                    [
                                                                        dcc.Dropdown(
                                                                            options=[
                                                                                {
                                                                                    "label": "Issued",
                                                                                    "value": "Issued",
                                                                                },
                                                                                {
                                                                                    "label": "Retired",
                                                                                    "value": "Retired",
                                                                                },
                                                                            ],
                                                                            value="Issued",
                                                                            id="issued_or_retired",
                                                                            placeholder="Select Summary Type",
                                                                        )
                                                                    ],
                                                                    style={
                                                                        "padding-top": "0px"
                                                                    },
                                                                ),
                                                            ],
                                                            style={
                                                                "padding-top": "0px"
                                                            },
                                                        )
                                                    ],
                                                    lg=12,
                                                    md=12,
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=12,
                ),
                dbc.Col(),
            ],
            style=BETWEEN_SECTION_STYLE,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    id="offchain-volume-title", className="card-title"
                                ),
                                dbc.CardBody(dcc.Graph(id="offchain-volume-plot")),
                            ]
                        )
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    id="onchain-volume-title", className="card-title"
                                ),
                                dbc.CardBody(dcc.Graph(id="onchain-volume-plot")),
                            ]
                        )
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    id="on_vs_off_vintage_title", className="card-title"
                                ),
                                dbc.CardBody(dcc.Graph(id="on_vs_off_vintage_plot")),
                                dbc.CardFooter(
                                    id="on_vs_off_vintage_footer",
                                    className="on_vs_off_footers",
                                ),
                            ]
                        )
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    id="on_vs_off_origin_title", className="card-title"
                                ),
                                dbc.CardBody(dcc.Graph(id="on_vs_off_origin_plot")),
                                dbc.CardFooter(
                                    id="on_vs_off_origin_footer",
                                    className="on_vs_off_footers",
                                ),
                            ]
                        )
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    id="on_vs_off_project_title", className="card-title"
                                ),
                                dbc.CardBody(dcc.Graph(id="on_vs_off_project_plot")),
                                dbc.CardFooter(
                                    id="on_vs_off_project_footer",
                                    className="on_vs_off_footers",
                                ),
                            ]
                        )
                    ],
                    width=12,
                ),
            ]
        ),
    ]
    return content
