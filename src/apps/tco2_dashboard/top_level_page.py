from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_top_level_content(token_cg_dict, bridges_info_dict, df_prices, df_verra,
                             fig_historical_prices, fig_bridges_pie_chart):

    sum_total_tokenized = sum(d['Tokenized Quantity']
                              for d in bridges_info_dict.values())
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
                    int(token_cg_dict[i]["Current_Supply"])), className="card-text")
            ]), width=12)

        pool_card = dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5(token_cg_dict[i]["Full Name"])),
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
                        html.H1("State of Tokenized Carbon", className='page-title'))
                ]), width=12, style={'textAlign': 'center'})),
        dbc.Row([
            dbc.Col(dbc.Card([
                html.H5("Verra Registry credits ever Issued",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df_verra["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("Verra Registry credits ever Tokenized",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(sum_total_tokenized)), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("Percentage of Tokenized Credits",
                        className="card-title"),
                dbc.CardBody("{:.2%}".format(
                    (sum_total_tokenized / df_verra["Quantity"].sum())),
                    className="card-text")
            ]), lg=4, md=12),
        ], style={'paddingTop': '60px'}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Breakdown of Tokenized credits by Bridges",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_bridges_pie_chart))
                ], className="card-graph")
            ], width=12),
        ]),

        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("State of Carbon Pools", className='page-title'))
                ]), width=12, style={'textAlign': 'center'}
            ),
            style={'paddingTop': '60px'}),

        dbc.Row(
            pool_cards
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
