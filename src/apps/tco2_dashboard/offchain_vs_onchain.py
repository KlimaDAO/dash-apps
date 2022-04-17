from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def create_offchain_vs_onchain_content(bridges_info_dict, df_verra,
                                       fig_bridges_pie_chart, fig_on_vs_off_vintage,
                                       fig_on_vs_off_map, fig_on_vs_off_project, verra_fallback_note):

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

    sum_total_tokenized = sum(d['Tokenized Quantity']
                              for d in bridges_info_dict.values())
    content = [
        header,
        dbc.Row([
            dbc.Col(dbc.Card([
                html.H5("Verra Registry Credits Ever Issued",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df_verra["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("Verra Registry Credits Ever Tokenized",
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
                    html.H5("Breakdown of Tokenized Credits by Bridges",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_bridges_pie_chart))
                ])
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Credits Tokenized vs. Credits Issued by Vintage Start Dates",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_on_vs_off_vintage))
                ])
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Credits Tokenized vs. Credits Issued by Origin",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_on_vs_off_map))
                ])
            ], width=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Credits Tokenized vs. Credits Issued by Project Type",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=fig_on_vs_off_project))
                ])
            ], width=12),
        ]),
    ]
    return content
