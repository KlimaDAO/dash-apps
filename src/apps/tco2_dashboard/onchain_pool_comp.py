from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_onchain_pool_comp_content(tokens_dict, df_prices, fig_historical_prices):

    historical_price_note = "Note: The chart shows MCO2 prices based on the KLIMA/MCO2 pool since it launched."
    pool_cards = []
    for i in tokens_dict.keys():
        filtered_df = df_prices[~df_prices[f"{i}_Price"].isna()]
        bridge_name = tokens_dict[i]["Bridge"]
        if i == "MCO2":
            selective_cost_value = "NA"
            selective_cost_tooltip_text = (
                "There is no selective redemption/retirement functionality for MCO2."
            )
        else:
            fee_redeem_percentage = "{:.2%}".format(tokens_dict[i]["Fee Redeem Factor"])
            selective_cost_value = "${:.2f}".format(
                filtered_df[f"{i}_Price"].iloc[0]
                * (1 + tokens_dict[i]["Fee Redeem Factor"])
            )
            selective_cost_tooltip_text = f"This cost includes the asset spot price + \
                the {fee_redeem_percentage} fee to \
                selectively redeem or retire an underlying carbon project charged by \
                    {bridge_name}."
        price_col = dbc.Col(
            dbc.Card(
                [
                    html.H5("Price", className="card-title"),
                    dbc.CardBody(
                        "${:.2f}".format(filtered_df[f"{i}_Price"].iloc[0]),
                        className="card-text",
                    ),
                ]
            ),
            width=12,
        )

        selective_cost_col = dbc.Col(
            dbc.Card(
                [
                    html.Div(
                        [
                            html.H5("Selective Cost", className="card-title"),
                            html.Div(
                                html.Span(
                                    "info",
                                    className="material-icons-outlined",
                                    style={"font-size": "20px"},
                                    id=f"selective-cost-tooltip_{i}",
                                ),
                                className="tooltip-icon-container",
                            ),
                            dbc.Tooltip(
                                selective_cost_tooltip_text,
                                target=f"selective-cost-tooltip_{i}",
                                className="selective-cost-tooltip",
                                placement="top",
                                style={"background-color": "#303030"},
                            ),
                        ],
                        className="card-title-with-tooltip",
                    ),
                    dbc.CardBody(
                        selective_cost_value,
                        className="card-text",
                    ),
                ]
            ),
            width=12,
        )

        current_supply_col = dbc.Col(
            dbc.Card(
                [
                    html.H5("Current Supply", className="card-title"),
                    dbc.CardBody(
                        "{:,}".format(int(tokens_dict[i]["Current Supply"])),
                        className="card-text",
                    ),
                ]
            ),
            width=12,
        )

        pool_card = dbc.Col(
            [
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5(tokens_dict[i]["Full Name"] + f" ({i})")
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
                            html.H1("Carbon Prices", className="page-title")
                        ),
                    ]
                ),
                width=12,
                style={"textAlign": "center"},
            ),
        ),
        dbc.Row(pool_cards[:3], style={"paddingTop": "60px"}),
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
                                    style={"paddingTop": "10px"},
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
