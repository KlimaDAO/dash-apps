from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from helpers import (date_manipulations, black_list_manipulations,
                     filter_carbon_pool)
from Figures_Carbon_Pool import deposited_over_time, redeemed_over_time
from data_related_constants import redeems_rename_map, deposits_rename_map
from import_data import get_data_pool

df_deposited, df_redeemed = get_data_pool()

# rename_columns
df_deposited = df_deposited.rename(columns=deposits_rename_map)
df_redeemed = df_redeemed.rename(columns=redeems_rename_map)
# datetime manipulations
df_deposited = date_manipulations(df_deposited)
df_redeemed = date_manipulations(df_redeemed)
# Blacklist manipulations
# df_deposited = black_list_manipulations(df_deposited)
# df_redeemed = black_list_manipulations(df_redeemed)

# Carbon pool filter
BCT_deposited, BCT_redeemed = filter_carbon_pool(
    df_deposited, df_redeemed, "0x2f800db0fdb5223b3c3f354886d907a671414a7f")

# Figures
fig_deposited_over_time = deposited_over_time(BCT_deposited)
fig_redeemed_over_time = redeemed_over_time(BCT_redeemed)

content_BCT = [
    dbc.Row(
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H1("Toucan Protocol : Base Carbon Tonne Pool", className='page-title'))
            ]), width=8)
    ),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                html.H5("TCO2 tokens deposited", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(BCT_deposited["Quantity"].sum())), className="card-text")
            ]), width=4),
        dbc.Col(
            dbc.Card([
                html.H5("TCO2 tokens redeemed", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(BCT_redeemed["Quantity"].sum())), className="card-text")
            ]), width=4),
        dbc.Col(
            dbc.Card([
                html.H5("BCT tokens retired", className="card-title"),
                dbc.CardBody("Coming soon", className="card-text")
            ]), width=4),
    ], style={'padding-top': '96px'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.H5("TCO2 tokens deposited over time",
                        className="card-title"),
                dbc.CardBody(dcc.Graph(figure=fig_deposited_over_time))
            ], className="card-graph")
        ], width=4),
        dbc.Col([
                dbc.Card([
                    html.H5("TCO2 tokens redeemed over time",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_redeemed_over_time))
                ], className="card-graph")
                ], width=4),
        dbc.Col([
                dbc.Card([
                    html.H5("BCT tokens retired over time",
                            className="card-title"),
                    dbc.CardBody("Coming soon", className="card-text")
                ], className="card-graph"),
                ], width=4)
    ])
]
