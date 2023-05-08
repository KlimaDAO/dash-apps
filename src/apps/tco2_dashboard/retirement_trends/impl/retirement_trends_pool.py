from src.apps.tco2_dashboard.figures import (
    pool_klima_retirement_chart_stacked,
    pool_klima_retirement_table)
from src.apps.tco2_dashboard.helpers import (
    retirements_all_data_process,
    stacked_bar_chart_data_process,
    summary_table_data_process)
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_interface \
    import RetirementTrendsInterface
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types \
    import ChartContent, ListData, TopContent
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd 
import numpy as np


class RetirementTrendsByPool(RetirementTrendsInterface):

    def __init__(
            self,
            retirement_trend_inputs):

        self.df_carbon_metrics_polygon = \
            retirement_trend_inputs.df_carbon_metrics_polygon
        self.df_carbon_metrics_eth = \
            retirement_trend_inputs.df_carbon_metrics_eth
        self.raw_klima_retirements = \
            retirement_trend_inputs.raw_klima_retirements_df
        self.agg_daily_klima_retirements = \
            retirement_trend_inputs.daily_agg_klima_retirements_df

    def create_header(self) -> str:
        return "Retirement Trends By Pool"

    def create_top_content(self) -> TopContent:

        # BCT Redeemed Info
        bctRedeemed = float(
            self.df_carbon_metrics_polygon["carbonMetrics_bctRedeemed"].iloc[0]
        )

        bctKlimaRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_bctKlimaRetired"].iloc[0]
        )
        bctKlimaRedeemedRatio = bctKlimaRetired / bctRedeemed

        # NCT Redeemed Info
        nctRedeemed = float(
            self.df_carbon_metrics_polygon["carbonMetrics_nctRedeemed"].iloc[0]
        )

        nctKlimaRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_nctKlimaRetired"].iloc[0]
        )
        nctKlimaRedeemedRatio = nctKlimaRetired / nctRedeemed

        # UBO Redeemed Info
        uboRedeemed = float(
            self.df_carbon_metrics_polygon["carbonMetrics_uboRedeemed"].iloc[0]
        )

        uboKlimaRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_uboKlimaRetired"].iloc[0]
        )
        uboKlimaRedeemedRatio = uboKlimaRetired / uboRedeemed

        # NBO Redeemed Info
        nboRedeemed = float(
            self.df_carbon_metrics_polygon["carbonMetrics_nboRedeemed"].iloc[0]
        )

        nboKlimaRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_nboKlimaRetired"].iloc[0]
        )
        nboKlimaRedeemedRatio = nboKlimaRetired / nboRedeemed

        # MCO2 Retired Info
        mco2Retired = float(
            # Note: We are taking MCO2 retirements from ETH
            self.df_carbon_metrics_eth["carbonMetrics_mco2Retired"].iloc[0]
        )
        mco2KlimaRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_mco2KlimaRetired"].iloc[0]
        )
        mco2KlimaRetiredRatio = mco2KlimaRetired / mco2Retired

        redemption_tooltip_message = \
            "Percentage of Redemptions tied to Retirements made via KlimaDAO"

        top_content_data = \
            [dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "BCT",
                                    className="card-title-retirement-trends",
                                ),
                                html.H5(
                                    "Total Redemptions (Tonnes)",
                                    className="card-title-retirement-trends",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(bctRedeemed)),
                                    className="card-text-retirement-trends",
                                ),
                                html.Div(
                                    [
                                        html.H5("Percentage Redeemed via KlimaDAO",
                                                className="card-title-retirement-trends"),
                                        html.Div(
                                            html.Span(
                                                "info",
                                                className="material-icons-outlined",
                                                style={"font-size": "20px"},
                                                id="redeemed-via-klimadao-tooltip-bct",
                                            ),
                                            className="tooltip-icon-container",
                                        ),
                                        dbc.Tooltip(
                                            redemption_tooltip_message,
                                            target="redeemed-via-klimadao-tooltip-bct",
                                            className="redeemed-via-klimadao-tooltip",
                                            placement="top",
                                            style={
                                                "background-color": "#303030"},
                                        ),
                                    ],
                                    className="card-title-with-tooltip",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(bctKlimaRedeemedRatio),
                                    className="card-text-retirement-trends",
                                ),
                            ],
                        ),
                        lg=6,
                        md=12,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "NCT",
                                    className="card-title-retirement-trends",
                                ),
                                html.H5(
                                    "Total Redemptions (Tonnes)",
                                    className="card-title-retirement-trends",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(nctRedeemed)),
                                    className="card-text-retirement-trends",
                                ),
                                html.Div(
                                    [
                                        html.H5("Percentage Redeemed via KlimaDAO",
                                                className="card-title-retirement-trends"),
                                        html.Div(
                                            html.Span(
                                                "info",
                                                className="material-icons-outlined",
                                                style={"font-size": "20px"},
                                                id="redeemed-via-klimadao-tooltip-nct",
                                            ),
                                            className="tooltip-icon-container",
                                        ),
                                        dbc.Tooltip(
                                            redemption_tooltip_message,
                                            target="redeemed-via-klimadao-tooltip-nct",
                                            className="redeemed-via-klimadao-tooltip",
                                            placement="top",
                                            style={
                                                "background-color": "#303030"},
                                        ),
                                    ],
                                    className="card-title-with-tooltip",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(nctKlimaRedeemedRatio),
                                    className="card-text-retirement-trends",
                                ),
                            ],
                        ),
                        lg=6,
                        md=12,
                    ),
                ],
            ),
                dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "UBO",
                                    className="card-title-retirement-trends",
                                ),
                                html.H5(
                                    "Total Redemptions (Tonnes)",
                                    className="card-title-retirement-trends",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(uboRedeemed)),
                                    className="card-text-retirement-trends",
                                ),
                                html.Div(
                                    [
                                        html.H5(
                                            "Percentage Redeemed via KlimaDAO",
                                            className="card-title-retirement-trends"),
                                        html.Div(
                                            html.Span(
                                                "info",
                                                className="material-icons-outlined",
                                                style={"font-size": "20px"},
                                                id="redeemed-via-klimadao-tooltip-ubo",
                                            ),
                                            className="tooltip-icon-container",
                                        ),
                                        dbc.Tooltip(
                                            redemption_tooltip_message,
                                            target="redeemed-via-klimadao-tooltip-ubo",
                                            className="redeemed-via-klimadao-tooltip",
                                            placement="top",
                                            style={
                                                "background-color": "#303030"},
                                        ),
                                    ],
                                    className="card-title-with-tooltip",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(uboKlimaRedeemedRatio),
                                    className="card-text-retirement-trends",
                                ),
                            ],
                        ),
                        lg=6,
                        md=12,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "NBO",
                                    className="card-title-retirement-trends",
                                ),
                                html.H5(
                                    "Total Redemptions (Tonnes)",
                                    className="card-title-retirement-trends",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(nboRedeemed)),
                                    className="card-text-retirement-trends",
                                ),
                                html.Div(
                                    [
                                        html.H5(
                                            "Percentage Redeemed via KlimaDAO",
                                            className="card-title-retirement-trends"),
                                        html.Div(
                                            html.Span(
                                                "info",
                                                className="material-icons-outlined",
                                                style={"font-size": "20px"},
                                                id="redeemed-via-klimadao-tooltip-nbo",
                                            ),
                                            className="tooltip-icon-container",
                                        ),
                                        dbc.Tooltip(
                                            redemption_tooltip_message,
                                            target="redeemed-via-klimadao-tooltip-nbo",
                                            className="redeemed-via-klimadao-tooltip",
                                            placement="top",
                                            style={
                                                "background-color": "#303030"},
                                        ),
                                    ],
                                    className="card-title-with-tooltip",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(nboKlimaRedeemedRatio),
                                    className="card-text-retirement-trends",
                                ),
                            ],
                        ),
                        lg=6,
                        md=12,
                    ),
                ],
            ),
                dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "MCO2",
                                    className="card-title-retirement-trends",
                                ),
                                html.H5(
                                    "Total Retirements (Tonnes)",
                                    className="card-title-retirement-trends",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(mco2Retired)),
                                    className="card-text-retirement-trends",
                                ),
                                html.H5(
                                    "Percentage Retired via KlimaDAO",
                                    className="card-title-retirement-trends",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(mco2KlimaRetiredRatio),
                                    className="card-text-retirement-trends",
                                ),
                            ],
                        ),
                        lg=12,
                        md=12,
                    ),
                ],
            )]

        return TopContent(top_content_data)

    def create_chart_content(self) -> ChartContent:

        retirements_all = self.agg_daily_klima_retirements[
            self.agg_daily_klima_retirements[
                'dailyKlimaRetirements_token'].isin(
                    ["BCT", "MCO2", "NBO", "NCT", "UBO"])
        ]

        retirements_all = retirements_all_data_process(retirements_all)

        wrs = stacked_bar_chart_data_process(retirements_all)

        retirement_chart_figure = pool_klima_retirement_chart_stacked(wrs)

        summary_table = summary_table_data_process(retirements_all)

        summary_table_final = pool_klima_retirement_table(summary_table)

        content = dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5("KlimaDAO Retirements by Pool",
                                        className="card-title"),
                                dbc.CardBody(
                                    dcc.Graph(figure=retirement_chart_figure)),
                                dbc.CardBody(
                                    summary_table_final, style={
                                        "margin-top": "15px"})
                            ]
                        )
                    ],
                    width=12,
                ),
            ]
        )

        return ChartContent(content)

    def merge_daily_retirements_df(self, df):

        datetime_str = "dailyKlimaRetirements_datetime"
        amount_str = "dailyKlimaRetirements_amount"
        token_str = "dailyKlimaRetirements_token"

        tco2_df = df.loc[
            (df[token_str] == "BCT") |
            (df[token_str] == "NCT")].copy()

        tco2_df = tco2_df.assign(dailyKlimaRetirements_token='TCO2')
        tco2_df = tco2_df.groupby([datetime_str])[
            amount_str].sum().reset_index()

        c3t_df = df.loc[
            (df[token_str] == "UBO") |
            (df[token_str] == "NBO")].copy()

        c3t_df = c3t_df.assign(dailyKlimaRetirements_token='C3T')
        c3t_df = c3t_df.groupby([datetime_str])[amount_str].sum().reset_index()
        return tco2_df, c3t_df

    def create_list_data(self) -> ListData:
        klima_retirements_df = self.modify_klima_token_retirements_df(
            self.raw_klima_retirements
        )

        return ListData("Detailed list of KlimaDAO Retirements", klima_retirements_df)

    def modify_klima_token_retirements_df(self, df):
        df = df.rename(
            columns={
                'klimaRetires_beneficiaryAddress': 'Beneficiary Address',
                'klimaRetires_offset_projectID': 'Project',
                'klimaRetires_token': 'Pool',
                'klimaRetires_datetime': 'Date',
                'klimaRetires_proof': 'View on PolygonScan',
                'klimaRetires_amount': 'Amount in Tonnes'})

        df['Amount in Tonnes'] = df[
            'Amount in Tonnes'].round(3)
        df['Pledge'] = (
            '[Click Here](https://www.klimadao.finance/pledge/' +
            df['Beneficiary Address'] + ')'
        )
        df['View on PolygonScan'] = '[Click Here](' + df['View on PolygonScan'] + ')'

        df['Project_num'] = df['Project'].apply(
            lambda x: pd.Series(str(x).split("-"))
            )[1]

        df.Project_num.fillna('N/A', inplace=True)

        verra_l = 'https://registry.verra.org/app/projectDetail/VCS/'

        df['Project_Link'] = verra_l

        df["Project_Link"] = df["Project_Link"] + df["Project_num"]

        missing_condition_1 = df['Project_Link'].str.match(
            'https://registry.verra.org/app/projectDetail/VCS/N/A')

        df['Project_Link'] = np.where(
            missing_condition_1, "N/A", df['Project_Link']
            )

        missing_condition_2 = df['Project_num'].str.match("N/A")

        df['Project_Link'] = np.where(
            missing_condition_2,
            'N/A',
            "[" + df['Project'] + "]" + "(" + df['Project_Link'] + ")"
            )

        pools_condition = df['Pool'].str.match(
            "BCT|NBO|NCT|UBO|MCO2|0x0000000000000000000000000000000000000000")

        df['Pool'] = np.where(pools_condition, df['Pool'], 'N/A')

        df.drop(['Project', 'Project_num'], axis=1, inplace=True)

        df = df.rename(
              columns={
                    'Project_Link': 'Project'
              }
        )

        df = df[['Beneficiary Address',
                 'Project',
                 'Pool',
                 'Date',
                 'Amount in Tonnes',
                 'View on PolygonScan',
                 'Pledge']]

        return df

    def replace_klima_retirements_token_values(self, df):
        df['Pool'] = df['Pool'].replace(['BCT'], 'TCO2')
        df['Pool'] = df['Pool'].replace(['NCT'], 'TCO2')
        df['Pool'] = df['Pool'].replace(['UBO'], 'C3T')
        df['Pool'] = df['Pool'].replace(['NBO'], 'C3T')

        return df
