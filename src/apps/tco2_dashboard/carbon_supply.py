from dash import html, dash_table
from dash import dcc
import dash_bootstrap_components as dbc

from .constants import GRAY, DARK_GRAY


def create_carbon_supply_content(
    df_carbon_metrics_polygon,
    df_carbon_metrics_eth,
    df_carbon_metrics_celo,
    polygon_supply_figure,
    polygon_retirement_figure
):
    totalCarbonSupply = int(df_carbon_metrics_polygon["carbonMetrics_totalCarbonSupply"].iloc[0])
    totalKlimaRetired = float(df_carbon_metrics_polygon["carbonMetrics_totalKlimaRetirements"].iloc[0])
    totalRetired = float(df_carbon_metrics_polygon["carbonMetrics_totalRetirements"].iloc[0])

    klimaRetiredPercentage = totalKlimaRetired / totalRetired

    content = [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                "Polygon On Chain Carbon",
                                className="page-title",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center"},
            )
        ),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    html.H5("Total Supply In Tonnes",
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        totalCarbonSupply),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=6),
            dbc.Col(
                dbc.Card([
                    html.H5("Total Retirements In Tonnes",
                            className="card-title"),
                    dbc.CardBody("{:,}".format(
                        int(totalRetired)),
                        className="card-text"),
                    html.H5("Percentage Retired By Klima",
                            className="card-title"),
                    dbc.CardBody("{:.2%}".format(
                        klimaRetiredPercentage),
                        className="card-text")
                ], style={'margin': '0px', 'padding': '0px'}), width=6),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H5("Supply",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=polygon_supply_figure))
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    html.H5("Retirements",
                            className="card-title"),
                    dbc.CardBody(dcc.Graph(figure=polygon_retirement_figure))
                ])
            ], width=6),
        ]),
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             dbc.Card(
        #                 [
        #                     html.H5(
        #                         f"Cumulative Tonnes of {bridge_ticker} Deposited",
        #                         className="card-title",
        #                     ),
        #                     dbc.CardBody(
        #                         "{:,}".format(
        #                             int(deposited["Quantity"].sum())),
        #                         className="card-text",
        #                     ),
        #                 ],
        #                 className="card-pool-summary",
        #             ),
        #             lg=4,
        #             md=12,
        #         ),
        #         dbc.Col(
        #             dbc.Card(
        #                 [
        #                     html.H5(
        #                         f"Cumulative Tonnes of {bridge_ticker} Redeemed",
        #                         className="card-title",
        #                     ),
        #                     dbc.CardBody(
        #                         "{:,}".format(int(redeemed["Quantity"].sum())),
        #                         className="card-text",
        #                     ),
        #                 ],
        #                 className="card-pool-summary",
        #             ),
        #             lg=4,
        #             md=12,
        #         ),
        #         dbc.Col(retired_card, lg=4, md=12),
        #     ],
        #     style={"paddingTop": "60px"},
        # ),
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #                 dbc.Card(
        #                     [
        #                         html.H5(
        #                             f"Cumulative Tonnes of {bridge_ticker} Deposited Over Time",
        #                             className="card-title",
        #                         ),
        #                         dbc.CardBody(
        #                             dcc.Graph(figure=fig_deposited_over_time)),
        #                     ],
        #                     className="card-graph",
        #                 )
        #             ],
        #             lg=4,
        #             md=12,
        #         ),
        #         dbc.Col([redeemed_graph], lg=4, md=12),
        #         dbc.Col([retired_graph], lg=4, md=12),
        #     ]
        # ),
        # dbc.Row(
        #     [
        #         dbc.Col(),
        #         dbc.Col(
        #             dbc.Card(
        #                 [
        #                     dbc.CardBody(
        #                         html.H2(f"Deep Dive into {pool_ticker}"),
        #                         style={"textAlign": "center"},
        #                     )
        #                 ]
        #             ),
        #             lg=6,
        #             md=12,
        #         ),
        #         dbc.Col(),
        #     ],
        #     style={"paddingTop": "60px"},
        # ),
        # dbc.Row(
        #     [
        #         dbc.Col(),
        #         dbc.Col(
        #             dbc.Card(
        #                 [
        #                     html.H5(
        #                         "Distribution of Vintage Start Dates",
        #                         className="card-title",
        #                     ),
        #                     dcc.Graph(figure=fig_total_vintage),
        #                 ]
        #             ),
        #             width=12,
        #         ),
        #         dbc.Col(),
        #     ]
        # ),
        # dbc.Row(
        #     [
        #         dbc.Col(),
        #         dbc.Col(
        #             dbc.Card(
        #                 [
        #                     html.H5(
        #                         "Origin of Tokenized Credits", className="card-title"
        #                     ),
        #                     dcc.Graph(figure=fig_total_map),
        #                 ]
        #             ),
        #             width=12,
        #         ),
        #         dbc.Col(),
        #     ]
        # ),
        # dbc.Row(
        #     [
        #         dbc.Col(),
        #         dbc.Col(
        #             dbc.Card(
        #                 [
        #                     html.H5(
        #                         "Distribution of Methodologies", className="card-title"
        #                     ),
        #                     dcc.Graph(figure=fig_total_metho),
        #                 ]
        #             ),
        #             width=12,
        #         ),
        #         dbc.Col(),
        #     ]
        # ),
        # dbc.Row(
        #     [
        #         dbc.Col(),
        #         dbc.Col(
        #             dbc.Card(
        #                 [
        #                     html.H5("Distribution of Projects",
        #                             className="card-title"),
        #                     dcc.Graph(figure=fig_total_project),
        #                 ]
        #             ),
        #             width=12,
        #         ),
        #         dbc.Col(),
        #     ]
        # ),
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #                 dbc.Card(
        #                     [
        #                         html.H5(
        #                             f"{pool_ticker} Pool Composition Details",
        #                             className="card-title",
        #                         ),
        #                         dash_table.DataTable(
        #                             detail_df.to_dict("records"),
        #                             [
        #                                 {
        #                                     "name": i,
        #                                     "id": i,
        #                                     "presentation": "markdown",
        #                                     "type": table_type(i),
        #                                 }
        #                                 for i in detail_df.columns
        #                             ],
        #                             id="tbl",
        #                             style_header={
        #                                 "backgroundColor": GRAY,
        #                                 "text-align": "center",
        #                             },
        #                             style_data={
        #                                 "backgroundColor": DARK_GRAY,
        #                                 "color": "white",
        #                             },
        #                             style_data_conditional=[
        #                                 {
        #                                     "if": {"column_id": "Project ID"},
        #                                     "minWidth": "180px",
        #                                     "width": "180px",
        #                                     "maxWidth": "180px",
        #                                 },
        #                                 {
        #                                     "if": {"column_id": "Country"},
        #                                     "minWidth": "180px",
        #                                     "width": "180px",
        #                                     "maxWidth": "180px",
        #                                 },
        #                                 {
        #                                     "if": {"column_id": "Quantity"},
        #                                     "minWidth": "180px",
        #                                     "width": "180px",
        #                                     "maxWidth": "180px",
        #                                 },
        #                                 {
        #                                     "if": {"column_id": "Vintage"},
        #                                     "minWidth": "180px",
        #                                     "width": "180px",
        #                                     "maxWidth": "180px",
        #                                 },
        #                                 {
        #                                     "if": {"column_id": "Methodology"},
        #                                     "minWidth": "180px",
        #                                     "width": "180px",
        #                                     "maxWidth": "180px",
        #                                 },
        #                                 {
        #                                     "if": {"state": "active"},
        #                                     "backgroundColor": "#202020",
        #                                     "border": "1px solid #2a2a2a",
        #                                     "color": "white",
        #                                 },
        #                             ],
        #                             style_table={"overflowX": "auto"},
        #                             page_size=20,
        #                             sort_action="native",
        #                             filter_action="native",
        #                             style_filter={
        #                                 "backgroundColor": GRAY,
        #                             },
        #                         ),
        #                         dbc.Row(
        #                             [
        #                                 dbc.Col(
        #                                     html.Div(
        #                                         [
        #                                             html.Button(
        #                                                 html.Span(
        #                                                     "file_download",
        #                                                     className="material-icons",
        #                                                 ),
        #                                                 id="download_btn_"
        #                                                 + pool_ticker,
        #                                                 className="download_btn",
        #                                             ),
        #                                             dcc.Download(
        #                                                 id="download_csv_" + pool_ticker
        #                                             ),
        #                                         ],
        #                                         className="download_btn_div",
        #                                     ),
        #                                     width=4,
        #                                 ),
        #                             ],
        #                             style={"padding-top": "5px"},
        #                         ),
        #                     ]
        #                 )
        #             ]
        #         )
        #     ]
        # ),
    ]
    return content
