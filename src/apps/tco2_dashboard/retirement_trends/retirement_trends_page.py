from dash import html, dash_table
import dash_bootstrap_components as dbc
from src.apps.tco2_dashboard.retirement_trends import retirement_trends_types

from src.apps.tco2_dashboard.retirement_trends.retirement_trends_factory \
    import RetirementTrendsFactory
from ..constants import GRAY, DARK_GRAY

TYPE_POOL = retirement_trends_types.TYPE_POOL
TYPE_TOKEN = retirement_trends_types.TYPE_TOKEN
TYPE_CHAIN = retirement_trends_types.TYPE_CHAIN
TYPE_BENEFICIARY = retirement_trends_types.TYPE_BENEFICIARY


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
    chart_data = retirement_trends.create_chart_content()
    list_data = retirement_trends.create_list_data()

    content = [
        # Adding top nav row
        dbc.Row(
            dbc.Nav(
                [
                    dbc.NavLink(
                        [
                            html.Span(
                                "By Pool", className="nav-bar-retirement-trends"
                            ),
                        ],
                        href="/retirements",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Span(
                                "By Token", className="nav-bar-retirement-trends"
                            ),
                        ],
                        href="/retirements/token",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Span(
                                "By Chain", className="nav-bar-retirement-trends"
                            ),
                        ],
                        href="/retirements/chain",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [
                            html.Span(
                                "By Beneficiary", className="nav-bar-retirement-trends"
                            ),
                        ],
                        href="/retirements/beneficiary",
                        active="exact",
                    ),
                ],
                horizontal=True,
                pills=True),
            style={"margin-left": "20px"}),

        # Adding header rows
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H1(
                                header,
                                className="page-title-retirement-trends",
                            )
                        )
                    ]
                ),
                width=12,
                style={"textAlign": "center"},
            )
        )]
    # Adding top content rows
    if top_data_content is not None:
        for item in top_data_content.data:
            content.append(item)

    # Adding Klima Daily retirement Chart row
    if chart_data is not None:
        content.append(chart_data.data)

    # Adding Klima Retirement List row
    content.append(dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            html.H5(
                                list_data.header,
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
                                    'column_id': list_data.sort_column,
                                    'direction': 'desc'}],
                            ),
                        ],
                    )
                ]
            )
        ]
    ),
    )
    return content
