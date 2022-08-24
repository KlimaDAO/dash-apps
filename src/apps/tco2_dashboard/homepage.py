from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from datetime import date, datetime


def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )


def create_homepage_content(
    df_retired,
    df_offchain,
    df_offchain_retired,
    df_onchain,
    df_onchain_retired,
    df_retirements,
    df_holders,
    fig_on_vs_off_time,
    fig_retirements,
    fig_holders,
):
    curr_time_str = datetime.utcnow().strftime("%b %d %Y %H:%M:%S UTC")
    header_card = dbc.Card(
        [
            dbc.CardImg(
                src="/assets/homepage-title-background.jpg",
                top=True,
                style={"opacity": 1},
                className="overlay-image",
            ),
            dbc.CardImgOverlay(
                dbc.CardBody(
                    [
                        html.P(
                            [
                                html.P(
                                    [
                                        "LAST UPDATED",
                                        html.Br(),
                                        curr_time_str,
                                    ],
                                    className="overlay-image-lastupdated",
                                ),
                                html.P(
                                    [
                                        "The State of the Tokenized",
                                        html.Br(),
                                        "Carbon Market",
                                    ],
                                    className="overlay-image-title",
                                ),
                                html.P(
                                    [
                                        "Carbon credits are moving on-chain,",
                                        html.Br(),
                                        "follow its progress",
                                    ],
                                    className="overlay-image-subtitle",
                                ),
                            ],
                            className="overlay-image-card-texts",
                        )
                    ],
                    className="overlay-image-card",
                ),
            ),
        ],
        className="heading-card",
    )
    offchain = human_format(
        df_offchain["Quantity"].iloc[-1] + df_onchain["Quantity"].iloc[-1]
    )
    offchain_retired = human_format(df_offchain_retired["Quantity"].iloc[-1])
    onchain = human_format(df_onchain["Quantity"].iloc[-1])
    onchain_retired = human_format(df_onchain_retired["Quantity"].iloc[-1])
    highest_retirements = "{:,}".format(int(df_retirements["Quantity"].iloc[0]))
    highest_retirements_name = df_retirements["Beneficiary"].iloc[0]
    highest_holdings = "{:,}".format(int(df_holders["Quantity"].iloc[0]))
    highest_holdings_name = df_holders["Klimate Name"].iloc[0]

    today = date.today().strftime("%B %d, %Y")

    content = [
        dbc.Row(dbc.Col(header_card)),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                "The Voluntary Carbon Market",
                                className="vcm-card-header",
                            ),
                            dbc.CardBody(
                                "The VCM is a robust and effective means to tackle climate change by driving"
                                " resources to projects which deliver independently verified and additional"
                                " emissions reductions on a global scale.",
                                className="vcm-card-text",
                            ),
                        ],
                        className="vcm-card",
                    ),
                    lg=8,
                    md=12,
                ),
                dbc.Col(),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                f"As of {today}", className="summary-card-header"
                            ),
                            dbc.CardBody(
                                [
                                    html.Strong(offchain),
                                    " off-chain credits have been created, with ",
                                    html.Strong(offchain_retired),
                                    " retired. ",
                                    html.Strong(onchain),
                                    " credits have been brought on-chain, with ",
                                    html.Strong(onchain_retired),
                                    " retired.",
                                ],
                                className="summary-card-text",
                            ),
                        ],
                        className="summary-card",
                    ),
                    lg=8,
                    md=12,
                ),
                dbc.Col(),
            ],
            style={"padding-top": "60px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Img(
                                                src=fig_on_vs_off_time,
                                                className="offvson_fig",
                                            ),
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Div(
                                                [
                                                    html.Button(
                                                        html.Span(
                                                            "file_download",
                                                            className="material-icons",
                                                        ),
                                                        id="download_btn_carbonmarket",
                                                    ),
                                                    dcc.Download(
                                                        id="download_image_carbonmarket"
                                                    ),
                                                ],
                                                className="download_btn_div",
                                            ),
                                            width=2,
                                        ),
                                    ]
                                ),
                            ],
                            className="offvson_fig_card",
                        )
                    )
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Holdings", className="summary-card-header"),
                            dbc.CardBody(
                                [
                                    html.Strong(highest_holdings_name),
                                    " is holding ",
                                    html.Strong(highest_holdings),
                                    " carbon assets, making them the largest single holder of tokenized carbon assets.",
                                ],
                                className="summary-card-text",
                            ),
                        ],
                        className="summary-card",
                    ),
                    lg=8,
                    md=12,
                ),
                dbc.Col(),
            ],
            style={"padding-top": "45px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Img(
                                                src=fig_holders, className="img_fig"
                                            ),
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Div(
                                                [
                                                    html.Button(
                                                        html.Span(
                                                            "file_download",
                                                            className="material-icons",
                                                        ),
                                                        id="download_btn_holders",
                                                    ),
                                                    dcc.Download(
                                                        id="download_image_holders"
                                                    ),
                                                ],
                                                className="download_btn_div",
                                            ),
                                            width=2,
                                        ),
                                    ]
                                ),
                            ],
                            className="img_card_body",
                        ),
                    )
                )
            ],
            className="img_row",
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                "Retirements", className="summary-card-header"
                            ),
                            dbc.CardBody(
                                [
                                    "To date, ",
                                    html.Strong(highest_retirements_name),
                                    " has retired ",
                                    html.Strong(highest_retirements),
                                    " tokenized carbon credits, making them the current leader in tokenized carbon"
                                    " retirements.",
                                ],
                                className="summary-card-text",
                            ),
                        ],
                        className="summary-card",
                    ),
                    lg=8,
                    md=12,
                ),
                dbc.Col(),
            ],
            style={"padding-top": "45px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Img(
                                                src=fig_retirements, className="img_fig"
                                            ),
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Div(
                                                [
                                                    html.Button(
                                                        html.Span(
                                                            "file_download",
                                                            className="material-icons",
                                                        ),
                                                        id="download_btn_retirements",
                                                    ),
                                                    dcc.Download(
                                                        id="download_image_retirements"
                                                    ),
                                                ],
                                                className="download_btn_div",
                                            ),
                                            width=2,
                                        ),
                                    ]
                                ),
                            ],
                            className="img_card_body",
                        )
                    )
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Up next", className="summary-card-header"),
                            dbc.CardBody(
                                [
                                    "Off vs on-chain carbon",
                                    html.Div(
                                        html.A(
                                            html.Span(
                                                "keyboard_arrow_right",
                                                className="material-icons",
                                            ),
                                            href="/Carbonmarket",
                                        ),
                                        className="upnext-icon-container",
                                    ),
                                ],
                                className="upnext-card-text",
                            ),
                        ],
                        className="upnext-card",
                    ),
                    lg=10,
                    md=12,
                ),
                dbc.Col(),
            ],
            style={"padding-top": "45px"},
        ),
    ]

    return content
