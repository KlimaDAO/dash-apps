import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from helpers import (drop_duplicates, date_manipulations, black_list_manipulations,
                     region_manipulations, subsets)
from Figures import *
from data_related_constants import rename_map, retires_rename_map
# from get_data import execute
from import_data import get_data

df, df_retired = get_data()

# rename_columns
df = df.rename(columns=rename_map)
df_retired = df_retired.rename(columns=retires_rename_map)
# datetime manipulations
df = date_manipulations(df)
df_retired = date_manipulations(df_retired)
# Blacklist manipulations
# df = black_list_manipulations(df)
# df_retired = black_list_manipulations(df_retired)
# Region manipulations
df = region_manipulations(df)
df_retired = region_manipulations(df_retired)
# 7 day and 30 day subsets
sd_pool, last_sd_pool, td_pool, last_td_pool = subsets(df)
sd_pool_retired, last_sd_pool_retired, td_pool_retired, last_td_pool_retired = subsets(
    df_retired)

# drop duplicates data for Carbon Pool calculations
df_carbon = drop_duplicates(df)

# Summary
fig_pool_pie_chart = pool_pie_chart(df_carbon)

# Figures
# 7-day-performance
fig_seven_day_volume = sub_plots_volume(
    sd_pool, last_sd_pool, title_indicator="Credits Bridged (7d)", title_graph="")
fig_seven_day_volume_retired = sub_plots_volume(
    sd_pool_retired, last_sd_pool_retired, "Credits Retired (7d)", "")
fig_seven_day_vintage = sub_plots_vintage(
    sd_pool, last_sd_pool, "Average Credit Vintage (7d)", "")
fig_seven_day_vintage_retired = sub_plots_vintage(
    sd_pool_retired, last_sd_pool_retired, "Average Credit Vintage (7d)", "")
fig_seven_day_map = map(
    sd_pool, 'Where have the past 7-day credits originated from?')
fig_seven_day_map_retired = map(
    sd_pool_retired, 'Where were the past 7-day retired credits originated from?')
fig_seven_day_metho = methodology_volume_vs_region(sd_pool)
fig_seven_day_metho_retired = methodology_volume_vs_region(sd_pool_retired)


# 30-day-performance
fig_thirty_day_volume = sub_plots_volume(
    td_pool, last_td_pool, "Credits Bridged (30d)", "")
fig_thirty_day_volume_retired = sub_plots_volume(
    td_pool_retired, last_td_pool_retired, "Credits Retired (30d)", "")
fig_thirty_day_vintage = sub_plots_vintage(
    td_pool, last_td_pool, "Average Credit Vintage (30d)", "")
fig_thirty_day_vintage_retired = sub_plots_vintage(
    td_pool_retired, last_td_pool_retired, "Average Credit Vintage (30d)", "")
fig_thirty_day_map = map(
    td_pool, 'Where have the past 30-day credits originated from?')
fig_thirty_day_map_retired = map(
    td_pool_retired, 'Where were the past 30-day retired credits originated from?')
fig_thirty_day_metho = methodology_volume_vs_region(td_pool)
fig_thirty_day_metho_retired = methodology_volume_vs_region(td_pool_retired)

# Total
fig_total_volume = total_volume(df)
fig_total_volume_retired = total_volume(df_retired)
fig_total_vintage = total_vintage(df)
fig_total_vintage_retired = total_vintage(df_retired)
fig_total_map = map(df, 'Where have all the past credits originated from?')
fig_total_map_retired = map(
    df_retired, 'Where were all the past retired credits originated from?')
fig_total_metho = methodology_volume_vs_region(df)
fig_total_metho_retired = methodology_volume_vs_region(df_retired)


# Dashboard
# app = dash.Dash(__name__)

#
content_Toucan = [
    dbc.Row(
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H1("Toucan Carbon Credits Dashboard", className='page-title'))
            ]), width=8, style={'padding-top': '30px'})
    ),

    dbc.Row([
        dbc.Col(dbc.Card([
            html.H5("Bridged Tokenized Credits", className="card-title"),
            dbc.CardBody("{:,}".format(
                int(df["Quantity"].sum())), className="card-text")
        ]), width=4),
        dbc.Col(dbc.Card([
            html.H5("Retired Tokenized Credits", className="card-title"),
            dbc.CardBody("{:,}".format(
                int(df_retired["Quantity"].sum())), className="card-text")
        ]), width=4),
        dbc.Col(dbc.Card([
            html.H5("Current Supply of Tokenized Credits",
                    className="card-title"),
            dbc.CardBody("{:,}".format(
                int(df["Quantity"].sum()-df_retired["Quantity"].sum())), className="card-text")
        ]), width=4),
    ], style={'padding-top': '60px'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.H5("Composition of Carbon Pool", className="card-title"),
                dbc.CardBody(dcc.Graph(figure=fig_pool_pie_chart))
            ], className="card-graph")
        ], width=6),
        dbc.Col([
            dbc.Card([
                html.H5("Conversion to Eligible Ratio of a specific Carbon Pool",
                        className="card-title"),
                dbc.CardBody([dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(options=[{'label': 'BCT', 'value': 'BCT'},
                                              {'label': 'NCT', 'value': 'NCT'}], value='BCT', id='pie_chart_summary', placeholder='Select Carbon Pool', style=dict(font=dict(color='black'))), width=2), dbc.Col([dcc.Graph(id="eligible pie chart plot")], width=10)])
                              ])
            ], className="card-graph")
        ], width=6),
    ]),

    dbc.Row([
        dbc.Card([
            dbc.CardHeader(html.H2("Deep Dive into TCO2")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H5("Select Performance Range", className="card-title"),),
                            dbc.CardBody([dcc.Dropdown(options=[{'label': 'Last 7 Days Performance', 'value': 'Last 7 Days Performance'},
                                                                {'label': 'Last 30 Days Performance',
                                                                 'value': 'Last 30 Days Performance'},
                                                                {'label': 'Overall Performance', 'value': 'Overall Performance'}], value='Overall Performance', id='summary_type', placeholder='Select Summary Type')])
                        ])
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H5("Bridged or Retired TCO2s?", className="card-title"),),
                            dbc.CardBody([dcc.Dropdown(options=[{'label': 'Bridged', 'value': 'Bridged'},
                                                                {'label': 'Retired', 'value': 'Retired'}], value='Bridged', id='bridged_or_retired', placeholder='Select Summary Type')])
                        ])
                    ], width=6)
                ])
            ])
        ])
    ], style={'padding-top': '60px'}),


    dbc.Row([
        dbc.Col(),
        dbc.Col(dbc.Card([
            dbc.CardBody(html.H2(id="Last X Days"),
                         style={'textAlign': 'center'})
        ]), width=6),
        dbc.Col(),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            html.H5("Distribution of Volume", className="card-title"),
            dcc.Graph(id="volume plot")
        ]), width=6),
        dbc.Col(dbc.Card([
            html.H5("Distribution of Vintage", className="card-title"),
            dcc.Graph(id="vintage plot")
        ]), width=6),
    ]),

    dbc.Row([
        dbc.Col(),
        dbc.Col(dbc.Card([
            html.H5("Distribution of Region", className="card-title"),
            dcc.Graph(id="map")
        ]), width=12),
        dbc.Col(),
    ]),

    dbc.Row([
        dbc.Col(),
        dbc.Col(dbc.Card([
            html.H5("Distribution of Methodology", className="card-title"),
            html.Div(id="fig_total_metho")
        ]), width=12),
        dbc.Col(),
    ]),

    dbc.Row([], style={'padding-top': '96px'})
]
