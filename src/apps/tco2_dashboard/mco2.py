from dash import html, dash_table
from dash import dcc
import dash_bootstrap_components as dbc
from .constants import GRAY, DARK_GRAY


def create_content_moss(df_mco2_bridged, df_mco2_retired, fig_mco2_total_volume, fig_mco2_total_vintage,
                        fig_mco2_total_map, fig_mco2_total_metho,
                        fig_mco2_total_project):
    df_mco2_bridged = df_mco2_bridged[[
        'Project ID', 'Quantity', 'Vintage', 'Country', 'Project Type', 'Methodology', 'Name']]
    df_grouped = df_mco2_bridged.groupby(['Project ID', 'Country', 'Methodology', 'Project Type', 'Name', 'Vintage'])[
        'Quantity'].sum().to_frame().reset_index()

    def table_type(df_column):
        if [df_column] in [
                'Vintage', 'Quantity']:
            return 'numeric'
        else:
            return 'text'

    content_mco2 = [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H1("State of Moss Tokenized Carbon", className='page-title'))
                ]), width=12, style={'textAlign': 'center'})
        ),

        dbc.Row([
            dbc.Col(dbc.Card([
                html.H5("MCO2 Tonnes Bridged", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df_mco2_bridged["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("MCO2 Tonnes Retired", className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df_mco2_retired["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("MCO2 Tonnes Outstanding",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(df_mco2_bridged["Quantity"].sum() - df_mco2_retired["Quantity"].sum())), className="card-text")
            ]), lg=4, md=12),
        ], style={'paddingTop': '60px'}),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                dbc.CardBody(html.H2('Deep Dive into Bridged MCO2'),
                             style={'textAlign': 'center'})
            ]), lg=6, md=12),
            dbc.Col(),
        ], style={'paddingTop': '60px'}),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Cumulative Tonnes Bridged Over Time",
                        className="card-title"),
                dcc.Graph(figure=fig_mco2_total_volume)
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Vintage Start Dates",
                        className="card-title"),
                dcc.Graph(figure=fig_mco2_total_vintage)
            ]), width=12),
            dbc.Col(),
        ]),

        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Origin of Tokenized Credits",
                        className="card-title"),
                dcc.Graph(figure=fig_mco2_total_map)
            ]), width=12),
            dbc.Col(),
        ]),
        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Methodologies",
                        className="card-title"),
                dcc.Graph(figure=fig_mco2_total_metho)
            ]), width=12),
            dbc.Col(),
        ]),
        dbc.Row([
            dbc.Col(),
            dbc.Col(dbc.Card([
                html.H5("Distribution of Projects", className="card-title"),
                dcc.Graph(figure=fig_mco2_total_project)
            ]), width=12),
            dbc.Col(),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5('MCO2 Composition Details',
                            className="card-title"),
                    dash_table.DataTable(
                        df_grouped.to_dict('records'),
                        [{"name": i, "id": i, "presentation": "markdown", 'type': table_type(i)}
                            for i in df_mco2_bridged.columns],
                        id='tbl',
                        style_header={
                            'backgroundColor': GRAY,
                            'text-align': 'center'
                        },
                        style_data={
                            'backgroundColor': DARK_GRAY,
                            'color': 'white'
                        },
                        style_table={'overflowX': 'auto'},
                        style_data_conditional=[
                            {"if": {'column_id': 'Project ID'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {'column_id': 'Country'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {'column_id': 'Quantity'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {'column_id': 'Vintage'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {'column_id': 'Methodology'},
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             },
                            {"if": {"state": "active"},
                             "backgroundColor": "#202020",
                             "border": "1px solid #2a2a2a",
                             "color": "white",
                             },
                        ],
                        page_size=20,
                        sort_action='native',
                        filter_action='native',
                        style_filter={
                            'backgroundColor': GRAY,
                        }
                    ),
                ])
            ])
        ])
    ]
    return content_mco2
