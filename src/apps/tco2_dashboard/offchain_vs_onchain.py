from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_offchain_vs_onchain_content(bridges_info_dict, retires_info_dict, df_verra, df_verra_retired,
                                       fig_bridges_pie_chart, verra_fallback_note):

    if verra_fallback_note != "":
        header = dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("State of Tokenized Carbon")),
                    dbc.CardFooter(
                        verra_fallback_note,
                        id="fallback_indicator")
                ]), width=12, style={'textAlign': 'center'}),
        )
    else:
        header = dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("State of Tokenized Carbon")),
                ]), width=12, style={'textAlign': 'center'}),
        )

    sum_total_tokenized = sum(d['Dataframe']['Quantity'].sum()
                              for d in bridges_info_dict.values())
    sum_total_onchain_retired = sum(d['Dataframe']['Quantity'].sum()
                                    for d in retires_info_dict.values())

    offchain_retired_card = dbc.Col([
        dbc.Card([
            dbc.Col(
                dbc.Card([
                    html.H5('Off-Chain Verra Registry Credits Retired',
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(df_verra_retired['Quantity'].sum())), className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=12),
            dbc.Col(
                dbc.Card([
                    html.H5("Percentage of Retired Credits",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        df_verra_retired['Quantity'].sum()/(df_verra['Quantity'].sum() - sum_total_tokenized)),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=12),
        ])
    ], lg=6, md=12)

    onchain_retired_card = dbc.Col([
        dbc.Card([
            dbc.Col(
                dbc.Card([
                    html.H5('On-Chain Verra Registry Credits Retired',
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(sum_total_onchain_retired)), className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=12),
            dbc.Col(
                dbc.Card([
                    html.H5("Percentage of Retired Credits",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        sum_total_onchain_retired/sum_total_tokenized),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=12),
        ])
    ], lg=6, md=12)

    content = [
        header,
        dbc.Row([
            dbc.Col(dbc.Card([
                html.H5("Verra Registry Credits Issued",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df_verra["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("Verra Registry Credits Tokenized",
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
        ], style={'padding-top': '60px'}),
        dbc.Row([
            offchain_retired_card,
            onchain_retired_card
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Breakdown of Tokenized Credits by Bridges",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_bridges_pie_chart))
                ])
            ], width=12),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H2("Deep Dive into Off-Chain vs On-Chain Carbon Credits")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader(
                                        html.H5("Issued or Retired Credits?", className="card-title"),),
                                    dbc.CardBody([dcc.Dropdown(options=[{'label': 'Issued', 'value': 'Issued'},
                                                                        {'label': 'Retired', 'value': 'Retired'}],
                                                               value='Issued', id='issued_or_retired',
                                                               placeholder='Select Summary Type')])
                                ])
                            ], lg=12, md=12),
                        ])
                    ])
                ]),
            ], width=12),
            dbc.Col()
        ], style={'paddingTop': '60px'}),


        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5(id='offchain-volume-title',
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(id='offchain-volume-plot'))
                ])
            ], width=12),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5(id='onchain-volume-title',
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(id='onchain-volume-plot'))
                ])
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5(id='on_vs_off_vintage_title',
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(id='on_vs_off_vintage_plot')),
                    dbc.CardFooter(id='on_vs_off_vintage_footer',
                                   className='on_vs_off_footers'),
                ])
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5(id='on_vs_off_origin_title',
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(id='on_vs_off_origin_plot')),
                    dbc.CardFooter(id='on_vs_off_origin_footer',
                                   className='on_vs_off_footers'),
                ])
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5(id='on_vs_off_project_title',
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(id='on_vs_off_project_plot')),
                    dbc.CardFooter(id='on_vs_off_project_footer',
                                   className='on_vs_off_footers'),
                ])
            ], width=12),
        ]),
    ]
    return content
