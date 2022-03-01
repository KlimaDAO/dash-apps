from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_content_toucan(df, df_retired, fig_pool_pie_chart):
    content_tco2 = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("Toucan Carbon Credits Dashboard", className='page-title'))
                ]), width=9, style={'padding-top': '30px'})
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
                html.H5("Current Supply",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df["Quantity"].sum()-df_retired["Quantity"].sum())), className="card-text")
            ]), width=4),
        ], style={'padding-top': '60px'}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Composition of Carbon Pool",
                            className="card-title"),
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
                                                  {'label': 'NCT', 'value': 'NCT'}], value='BCT',
                                         id='pie_chart_summary', placeholder='Select Carbon Pool',
                                         style=dict(font=dict(color='black'))), width=3),
                        dbc.Col([dcc.Graph(id="eligible pie chart plot")], width=9)])
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
                                dbc.CardBody([dcc.Dropdown(options=[{'label': 'Last 7 Days Performance',
                                                                     'value': 'Last 7 Days Performance'},
                                                                    {'label': 'Last 30 Days Performance',
                                                                    'value': 'Last 30 Days Performance'},
                                                                    {'label': 'Overall Performance',
                                                                     'value': 'Overall Performance'}],
                                                           value='Overall Performance', id='summary_type',
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
    return content_tco2
