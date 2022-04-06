from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_onchain_pool_comp_content(token_cg_dict, df_prices, fig_historical_prices):

    pool_cards = []
    for i in token_cg_dict.keys():
        price_col = dbc.Col(
            dbc.Card([
                html.H5("Price", className="card-title"),
                dbc.CardBody("${:.2f}".format(
                    df_prices[f"{i}_Price"].iloc[0]), className="card-text")
            ]), width=12)

        current_supply_col = dbc.Col(
            dbc.Card([
                html.H5("Current Supply", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(token_cg_dict[i]["Current Supply"])), className="card-text")
            ]), width=12)

        pool_card = dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H5(token_cg_dict[i]["Full Name"] + f' ({i})')),
                price_col,
                current_supply_col
            ])
        ], lg=(12/len(token_cg_dict.keys())), md=12)

        pool_cards.append(pool_card)

    content = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("State of Carbon Pools", className='page-title')),
                ]), width=12, style={'textAlign': 'center'}
            ),
        ),

        dbc.Row(
            pool_cards, style={'paddingTop': '60px'}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Historical Price Chart",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_historical_prices))
                ], className="card-graph")
            ], width=12),
        ]),
    ]
    return content
