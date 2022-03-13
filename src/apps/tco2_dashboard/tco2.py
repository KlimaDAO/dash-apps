from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_content_toucan(df, df_retired, fig_pool_pie_chart):
    content_tco2 = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("State of Toucan Tokenized Carbon", className='page-title'))
                ]), width=12, style={'textAlign': 'center'})
        ),

        dbc.Row([
            dbc.Col(dbc.Card([
                html.H5("TCO2 Tonnes Bridged", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df["Quantity"].sum())), className="card-text")
            ]), width=4),
            dbc.Col(dbc.Card([
                html.H5("TCO2 Tonnes Retired", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df_retired["Quantity"].sum())), className="card-text")
            ]), width=4),
            dbc.Col(dbc.Card([
                html.H5("TCO2 Tonnes Outstanding",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df["Quantity"].sum()-df_retired["Quantity"].sum())), className="card-text")
            ]), width=4),
        ], style={'paddingTop': '60px'}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Breakdown of TCO2 Pooled",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_pool_pie_chart))
                ], className="card-graph")
            ], width=12),
            # TODO: add methodology filter for NCT before re-enabling
            # dbc.Col([
            #     dbc.Card([
            #         html.H5("Conversion to Eligible Ratio of a specific Carbon Pool",
            #                 className="card-title"),
            #         dbc.CardBody([dbc.Row([
            #             dbc.Col(
            #                 dcc.Dropdown(options=[{'label': 'BCT', 'value': 'BCT'},
            #                                       {'label': 'NCT', 'value': 'NCT'}], value='BCT',
            #                              id='pie_chart_summary', placeholder='Select Carbon Pool',
            #                              style=dict(font=dict(color='black'))), width=3),
            #             dbc.Col([dcc.Graph(id="eligible pie chart plot")], width=9)])
            #                       ])
            #     ], className="card-graph")
            # ], width=6),
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
                                dbc.CardBody([dcc.Dropdown(options=[{'label': 'Last 7 Days Performance',
                                                                     'value': 'Last 7 Days Performance'},
                                                                    {'label': 'Last 30 Days Performance',
                                                                    'value': 'Last 30 Days Performance'},
                                                                    {'label': 'Lifetime Performance',
                                                                     'value': 'Lifetime Performance'}],
                                                           value='Lifetime Performance', id='summary_type',
                                                           placeholder='Select Summary Type')])
                            ])
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(
                                    html.H5("Bridged or Retired TCO2s?", className="card-title"),),
                                dbc.CardBody([dcc.Dropdown(options=[{'label': 'Bridged', 'value': 'Bridged'},
                                                                    {'label': 'Retired', 'value': 'Retired'}],
                                                           value='Bridged', id='bridged_or_retired',
                                                           placeholder='Select Summary Type')])
                            ])
                        ], width=6)
                    ])
                ])
            ])
        ], style={'paddingTop': '60px'}),


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
                html.H5("Volume Over Time", className="card-title"),
                dcc.Graph(id="volume plot")
            ]), width=6),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Vintage Start Dates", className="card-title"),
                dcc.Graph(id="vintage plot")
            ]), width=6),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Region of Origin", className="card-title"),
                dcc.Graph(id="map")
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Methodologies", className="card-title"),
                dcc.Graph(id="methodology")
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Projects", className="card-title"),
                dcc.Graph(id="projects")
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([], style={'paddingTop': '96px'})
    ]
    return content_tco2
