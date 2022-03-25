from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_top_level_content(token_cg_dict, df_prices, fig_historical_prices):

    price_cols = []
    current_supply_cols = []
    for i in token_cg_dict.keys():
        price_col = dbc.Col(
            dbc.Card([
                html.H5(f"Price of {i}", className="card-title"),
                dbc.CardBody("${:.2f}".format(
                    df_prices[f"{i}_Price"].iloc[0]), className="card-text")
            ]), lg=(12/len(token_cg_dict.keys())), md=12)

        price_cols.append(price_col)
        current_supply_col = dbc.Col(
            dbc.Card([
                html.H5(f"Current Supply of {i}", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(token_cg_dict[i]["Current_Supply"])), className="card-text")
            ]), lg=(12/len(token_cg_dict.keys())), md=12)

        current_supply_cols.append(current_supply_col)

    content = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("Top Level Summary of Carbon Pools", className='page-title'))
                ]), width=12, style={'textAlign': 'center'})),
        dbc.Row(
            price_cols, style={'paddingTop': '60px'}
        ),
        dbc.Row(
            current_supply_cols
        ),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Historical Price Chart",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_historical_prices))
                ], className="card-graph")
            ], width=12),
        ])
    ]
    return content
