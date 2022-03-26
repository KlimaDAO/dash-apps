from dash import html, dash_table
from dash import dcc
import dash_bootstrap_components as dbc
from .constants import GRAY, DARK_GRAY


def create_content_moss(df_mco2_bridged, fig_mco2_total_vintage, fig_mco2_total_map, fig_mco2_total_project,
                        current_supply):
    df_grouped = df_mco2_bridged.groupby(['Project ID', 'Country', 'Project Type', 'Name', 'Vintage'])[
        'Quantity'].sum().to_frame().reset_index()
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
                    int(df_mco2_bridged["Quantity"].sum() - current_supply)), className="card-text")
            ]), lg=4, md=12),
            dbc.Col(dbc.Card([
                html.H5("MCO2 Tonnes Outstanding",
                        className="card-title"),
                dbc.CardBody("{:,}".format(
                    int(current_supply)), className="card-text")
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
                        [{"name": i, "id": i, "presentation": "markdown"}
                            for i in df_mco2_bridged.columns],
                        id='tbl',
                        style_header={
                            'backgroundColor': GRAY,
                            'text-align': 'center'
                        },
                        style_data={
                            'backgroundColor': DARK_GRAY
                        },
                        style_table={'overflowX': 'auto'},
                        page_size=20,
                        sort_action='native'
                    ),
                ])
            ])
        ])
    ]
    return content_mco2
