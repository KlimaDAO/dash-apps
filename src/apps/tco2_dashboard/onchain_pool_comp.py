from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from .constants import BETWEEN_SECTION_STYLE
from .services import Tokens, Prices


def create_onchain_pool_comp_content(
    fig_historical_prices
):
    historical_price_note = "Note: The chart shows MCO2 prices based on the KLIMA/MCO2 pool since it launched."
    footer_style = {"paddingTop": "10px"}
    pool_cards = []
    tokens_dict = Tokens().get_dict()
    for token in tokens_dict.keys():
        filtered_df = Prices().token(token)
        bridge_name = tokens_dict[token]["Bridge"]
        if token == "MCO2":
            selective_cost_value = "NA"
            selective_cost_tooltip_text = (
                "There is no selective redemption/retirement functionality for MCO2."
            )
        else:
            fee_redeem_percentage = "{:.2%}".format(tokens_dict[token]["Fee Redeem Factor"])
            selective_cost_value = "${:.2f}".format(
                filtered_df["Price"].iloc[0]
                * (1 + tokens_dict[token]["Fee Redeem Factor"])
            )
            selective_cost_tooltip_text = f"This cost includes the asset spot price + \
                the {fee_redeem_percentage} fee to \
                selectively redeem or retire an underlying carbon project charged by \
                    {bridge_name}."
        price_col = dbc.Col(
            dbc.Card(
                [
                    html.H5("Price", className="card-title-price"),
                    dbc.CardBody(
                        "${:.2f}".format(filtered_df["Price"].iloc[0]),
                        className="card-text-continuation",
                    ),
                ],
                style={
                    "padding-top": "0px",
                    "padding-bottom": "0px",
                    "margin-top": "0px",
                    "margin-bottom": "0px",
                },
            ),
            width=12,
        )

        selective_cost_col = dbc.Col(
            dbc.Card(
                [
                    html.Div(
                        [
                            html.H5("Selective Cost", className="card-title-price"),
                            html.Div(
                                html.Span(
                                    "info",
                                    className="material-icons-outlined",
                                    style={"font-size": "20px"},
                                    id=f"selective-cost-tooltip_{token}",
                                ),
                                className="tooltip-icon-container",
                            ),
                            dbc.Tooltip(
                                selective_cost_tooltip_text,
                                target=f"selective-cost-tooltip_{token}",
                                className="selective-cost-tooltip",
                                placement="top",
                                style={"background-color": "#303030"},
                            ),
                        ],
                        className="card-title-with-tooltip",
                    ),
                    dbc.CardBody(
                        selective_cost_value,
                        className="card-text-continuation",
                    ),
                ],
                style={
                    "padding-top": "0px",
                    "padding-bottom": "0px",
                    "margin-top": "0px",
                    "margin-bottom": "0px",
                },
            ),
            width=12,
        )

        current_supply_col = dbc.Col(
            dbc.Card(
                [
                    html.H5("Current Supply", className="card-title-price"),
                    dbc.CardBody(
                        "{:,}".format(int(tokens_dict[token]["Current Supply"])),
                        className="card-text",
                    ),
                ],
                style={
                    "padding-top": "0px",
                    "padding-bottom": "0px",
                    "margin-top": "0px",
                    "margin-bottom": "0px",
                },
            ),
            width=12,
        )

        pool_card = dbc.Col(
            [
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(
                                tokens_dict[token]["Full Name"] + f" ({token})",
                                className="card-title",
                                style={"padding-bottom": "20px"},
                            ),
                        ),
                        price_col,
                        selective_cost_col,
                        current_supply_col,
                    ],
                    className="pool_card",
                )
            ],
            lg=(12 / min(len(tokens_dict.keys()), 3)),
            md=12,
        )
        pool_cards.append(pool_card)

    content = [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1("Digital Carbon Pricing", className="page-title")
                        ),
                    ]
                ),
                width=12,
                style={"textAlign": "center"},
            ),
        ),
        dbc.Row(pool_cards[:3], style=BETWEEN_SECTION_STYLE),
        dbc.Row(pool_cards[3:]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5("Historical Price", className="card-title"),
                                dbc.CardBody(dcc.Graph(figure=fig_historical_prices)),
                                dbc.CardFooter(
                                    historical_price_note,
                                    className="card-footer",
                                    style=footer_style,
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
