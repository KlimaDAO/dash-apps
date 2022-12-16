from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_content_c3t(df, df_retired, fig_pool_pie_chart):

    content_c3t = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader([
                        html.H1([
                            "State of ", 
                            str(),
                            "  ",
                            html.Span(
                                html.A(
                                    "C3 Tokenized Carbon", 
                                    href='https://docs.klimadao.finance/references/glossary#c3-token',
                                ), 
                                id="tooltip-target", 
                                style={"cursor": "pointer"} # "textDecoration": "underline", 
                            )
                        ], className='page-title'),

                        dbc.Tooltip("A utility token for the C3 carbon bridge. It is distributed as a reward to users of the protocol that stake, bridge or provide liquidity.",
                            target="tooltip-target",
                            style={"text-align": "right"},),
                    ])
                ]), width=12, style={'textAlign': 'center'}
            )
        ),

        dbc.Row([
            dbc.Col(dbc.Card([
                html.H5("C3T Tonnes Bridged", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("C3T Tonnes Retired", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df_retired["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("C3T Tonnes Outstanding",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df["Quantity"].sum()-df_retired["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
        ], style={'paddingTop': '60px'}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Breakdown of C3T Pooled",
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
            # ], lg=6, md=12),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H2([
                            "Deep Dive into ",
                            str(),
                            html.Span(
                                      html.A(
                                        "C3T", 
                                        href='https://docs.klimadao.finance/references/glossary#c3t',
                                      ),
                                      id="tooltip-target1", 
                                      style={"cursor": "pointer"} # "textDecoration": "underline", 
                                )
                            ], style={'textAlign': 'center'}),
                        dbc.Tooltip("C3 Tonne (C3T) is the general term for fungible tokenized carbon offsets bridged via C3.",
                                  target="tooltip-target1",
                                  style={"text-align": "right"},),
                    ]),
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
                                                               value='Lifetime Performance', id='summary_type_c3t',
                                                               placeholder='Select Summary Type')])
                                ])
                            ], lg=6, md=12),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader(
                                        html.H5("Bridged or Retired TCO2s?", className="card-title"),),
                                    dbc.CardBody([dcc.Dropdown(options=[{'label': 'Bridged', 'value': 'Bridged'},
                                                                        {'label': 'Retired', 'value': 'Retired'}],
                                                               value='Bridged', id='bridged_or_retired_c3t',
                                                               placeholder='Select Summary Type')])
                                ])
                            ], lg=6, md=12),
                        ])
                    ])
                ]),
            ], width=12),
            dbc.Col()
        ], style={'paddingTop': '60px'}),


        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                dbc.CardBody(html.H2(id="Last X Days_c3t"),
                             style={'textAlign': 'center'})
            ]), lg=6, md=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col(dbc.Card([
                html.H5("Volume Over Time", className="card-title"),
                dcc.Graph(id="volume plot_c3t")
            ]), lg=6, md=12),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Vintage Start Dates",
                        className="card-title"),
                dcc.Graph(id="vintage plot_c3t")
            ]), lg=6, md=12),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Origin of Credits", className="card-title"),
                dcc.Graph(id="map_c3t")
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Methodologies",
                        className="card-title"),
                dcc.Graph(id="methodology_c3t")
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Projects", className="card-title"),
                dcc.Graph(id="projects_c3t")
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([], style={'paddingTop': '96px'})
    ]
    return content_c3t
