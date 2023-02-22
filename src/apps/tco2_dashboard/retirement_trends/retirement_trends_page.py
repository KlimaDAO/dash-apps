from dash import html, dash_table
from dash import dcc
import dash_bootstrap_components as dbc
from src.apps.tco2_dashboard.retirement_trends import retirement_trends_types

from src.apps.tco2_dashboard.retirement_trends.retirement_trends_factory \
    import RetirementTrendsFactory
from ..constants import GRAY, DARK_GRAY

TYPE_POOL = retirement_trends_types.TYPE_POOL
TYPE_TOKEN = retirement_trends_types.TYPE_TOKEN
TYPE_CHAIN = retirement_trends_types.TYPE_CHAIN


def create_retirement_trend_inputs(
    df_carbon_metrics_polygon,
    df_carbon_metrics_eth,
    raw_klima_retirements_df,
    daily_agg_klima_retirements_df,
    verra_retired_df,
    df_verra,
    bridges_info_dict,
    verra_fallback_note
):

    return retirement_trends_types.RetirementTrendInputs(
        df_carbon_metrics_polygon,
        df_carbon_metrics_eth,
        raw_klima_retirements_df,
        daily_agg_klima_retirements_df,
        verra_retired_df,
        df_verra,
        bridges_info_dict,
        verra_fallback_note
    )


def create_content_retirement_trends(
    type,
    retirement_trend_inputs
):

    retirement_trends_factory = RetirementTrendsFactory(
        retirement_trend_inputs
    )

    retirement_trends = retirement_trends_factory.get_instance(type)

    header = retirement_trends.create_header()
    top_data_content = retirement_trends.create_top_content()
    chart_data = retirement_trends.create_chart_data()
    list_data = retirement_trends.create_list_data()

    content = [
        # Adding top nav
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Span(
                            "By Pool",
                        ),
                    ],
                    href="/retirements/pool",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.Span(
                            "By Token",
                        ),
                    ],
                    href="/retirements/token",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.Span(
                            "By Chain",
                        ),
                    ],
                    href="/retirements/chain",
                    active="exact",
                ),
            ],
            horizontal=True,
            pills=True,
            style={"gap": "4px"},),
        # Adding header rows
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                header,
                                className="page-title-carbon-supply",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center", "margin-bottom": "20px"},
            )
        )]
    # Adding top content rows
    for item in top_data_content.data:
        content.append(item)

    # Adding Klima Daily retirement Chart row
    content.append(dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            html.H5(chart_data.header,
                                    className="card-title"),
                            dbc.CardBody(
                                dcc.Graph(figure=chart_data.figure)),
                        ]
                    )
                ],
                width=12,
            ),
        ]
    ))
    # Adding Klima Retirement List row
    content.append(dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            html.H5(
                                "Detailed List of Retirements",
                                className="card-title",
                            ),
                            dash_table.DataTable(
                                list_data.dataframe.to_dict("records"),
                                [
                                    {
                                        "name": i,
                                        "id": i,
                                        "presentation": "markdown",
                                        "type": "text",
                                    }
                                    for i in list_data.dataframe.columns
                                ],
                                id="tbl",
                                style_header={
                                    "backgroundColor": GRAY,
                                    "text-align": "center",
                                },
                                style_data={
                                    "backgroundColor": DARK_GRAY,
                                    "color": "white",
                                },
                                style_table={"overflowX": "auto"},
                                page_size=20,
                                sort_action="native",
                                filter_action="native",
                                style_filter={
                                    "backgroundColor": GRAY,
                                },
                                sort_by=[{
                                    'column_id': 'Date', 'direction': 'desc'}],
                            ),
                        ]
                    )
                ]
            )
        ]
    ),
    )
    return content
