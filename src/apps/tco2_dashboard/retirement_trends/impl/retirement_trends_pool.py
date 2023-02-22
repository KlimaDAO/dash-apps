from src.apps.tco2_dashboard.figures import pool_klima_retirement_chart
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_interface \
     import RetirementTrendsInterface
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types \
    import ChartData, ListData, TopContent
import dash_bootstrap_components as dbc
from dash import html


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

        top_content_data = \
            [dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "BCT",
                                    className="card-title-carbon-supply",
                                ),
                                html.H5(
                                    "Total Redemptions (Tonnes)",
                                    className="card-title-carbon-supply",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(bctRedeemed)),
                                    className="card-text-carbon-supply",
                                ),
                                html.Div(
                                    [
                                        html.H5("Percentage Redeemed via KlimaDAO", className="card-title-carbon-supply"),
                                        html.Div(
                                            html.Span(
                                                "info",
                                                className="material-icons-outlined",
                                                style={"font-size": "20px"},
                                                id="selective-cost-tooltip-bct",
                                            ),
                                            className="tooltip-icon-container",
                                        ),
                                        dbc.Tooltip(
                                            "Percentage of Redemptions tied to Retirements made via KlimaDAO",
                                            target="selective-cost-tooltip-bct",
                                            className="selective-cost-tooltip",
                                            placement="top",
                                            style={"background-color": "#303030"},
                                        ),
                                    ],
                                    className="card-title-with-tooltip",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(bctKlimaRedeemedRatio),
                                    className="card-text-carbon-supply",
                                ),
                            ]
                        ),
                        lg=6,
                        md=12,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "NCT",
                                    className="card-title-carbon-supply",
                                ),
                                html.H5(
                                    "Total Redemptions (Tonnes)",
                                    className="card-title-carbon-supply",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(nctRedeemed)),
                                    className="card-text-carbon-supply",
                                ),
                                html.Div(
                                    [
                                        html.H5("Percentage Redeemed via KlimaDAO", className="card-title-carbon-supply"),
                                        html.Div(
                                            html.Span(
                                                "info",
                                                className="material-icons-outlined",
                                                style={"font-size": "20px"},
                                                id="selective-cost-tooltip-nct",
                                            ),
                                            className="tooltip-icon-container",
                                        ),
                                        dbc.Tooltip(
                                            "Percentage of Redemptions tied to Retirements made via KlimaDAO",
                                            target="selective-cost-tooltip-nct",
                                            className="selective-cost-tooltip",
                                            placement="top",
                                            style={"background-color": "#303030"},
                                        ),
                                    ],
                                    className="card-title-with-tooltip",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(nctKlimaRedeemedRatio),
                                    className="card-text-carbon-supply",
                                ),
                            ]
                        ),
                        lg=6,
                        md=12,
                    ),
                ],
                style={"margin-bottom": "20px"},
            ),
             dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "UBO",
                                    className="card-title-carbon-supply",
                                ),
                                html.H5(
                                    "Total Redemptions (Tonnes)",
                                    className="card-title-carbon-supply",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(uboRedeemed)),
                                    className="card-text-carbon-supply",
                                ),
                                html.Div(
                                    [
                                        html.H5("Percentage Redeemed via KlimaDAO", className="card-title-carbon-supply"),
                                        html.Div(
                                            html.Span(
                                                "info",
                                                className="material-icons-outlined",
                                                style={"font-size": "20px"},
                                                id="selective-cost-tooltip-ubo",
                                            ),
                                            className="tooltip-icon-container",
                                        ),
                                        dbc.Tooltip(
                                            "Percentage of Redemptions tied to Retirements made via KlimaDAO",
                                            target="selective-cost-tooltip-ubo",
                                            className="selective-cost-tooltip",
                                            placement="top",
                                            style={"background-color": "#303030"},
                                        ),
                                    ],
                                    className="card-title-with-tooltip",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(uboKlimaRedeemedRatio),
                                    className="card-text-carbon-supply",
                                ),
                            ]
                        ),
                        lg=6,
                        md=12,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "NBO",
                                    className="card-title-carbon-supply",
                                ),
                                html.H5(
                                    "Total Redemptions (Tonnes)",
                                    className="card-title-carbon-supply",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(nboRedeemed)),
                                    className="card-text-carbon-supply",
                                ),
                                html.Div(
                                    [
                                        html.H5("Percentage Redeemed via KlimaDAO", className="card-title-carbon-supply"),
                                        html.Div(
                                            html.Span(
                                                "info",
                                                className="material-icons-outlined",
                                                style={"font-size": "20px"},
                                                id="selective-cost-tooltip-nbo",
                                            ),
                                            className="tooltip-icon-container",
                                        ),
                                        dbc.Tooltip(
                                            "Percentage of Redemptions tied to Retirements made via KlimaDAO",
                                            target="selective-cost-tooltip-nbo",
                                            className="selective-cost-tooltip",
                                            placement="top",
                                            style={"background-color": "#303030"},
                                        ),
                                    ],
                                    className="card-title-with-tooltip",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(nboKlimaRedeemedRatio),
                                    className="card-text-carbon-supply",
                                ),
                            ]
                        ),
                        lg=6,
                        md=12,
                    ),
                ],
                style={"margin-bottom": "20px"},
            ),
             dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(
                                    "MCO2",
                                    className="card-title-carbon-supply",
                                ),
                                html.H5(
                                    "Total Retirements (Tonnes)",
                                    className="card-title-carbon-supply",
                                ),
                                dbc.CardBody(
                                    "{:,}".format(int(mco2Retired)),
                                    className="card-text-carbon-supply",
                                ),
                                html.H5(
                                    "Percentage Retired via KlimaDAO",
                                    className="card-title-carbon-supply",
                                ),
                                dbc.CardBody(
                                    "{:.2%}".format(mco2KlimaRetiredRatio),
                                    className="card-text-carbon-supply",
                                ),
                            ]
                        ),
                        lg=12,
                        md=12,
                    ),
                ],
                style={"margin-bottom": "20px"},
            )]

        return TopContent(top_content_data)

    def create_chart_data(self) -> ChartData:
        bct_df = self.agg_daily_klima_retirements[
            self.agg_daily_klima_retirements['dailyKlimaRetirements_token']
            == "BCT"]

        nct_df = self.agg_daily_klima_retirements[
            self.agg_daily_klima_retirements['dailyKlimaRetirements_token']
            == "NCT"]

        mco2_df = self.agg_daily_klima_retirements[
            self.agg_daily_klima_retirements['dailyKlimaRetirements_token']
            == "MCO2"]

        ubo_df = self.agg_daily_klima_retirements[
            self.agg_daily_klima_retirements['dailyKlimaRetirements_token']
            == "UBO"]

        nbo_df = self.agg_daily_klima_retirements[
            self.agg_daily_klima_retirements['dailyKlimaRetirements_token']
            == "NBO"]

        retirement_chart_figure = pool_klima_retirement_chart(
            bct_df,
            nct_df,
            mco2_df,
            ubo_df,
            nbo_df)

        return ChartData("Retirements by Pool", retirement_chart_figure)

    def merge_daily_retirements_df(self, df):

        datetime_str = "dailyKlimaRetirements_datetime"
        amount_str = "dailyKlimaRetirements_amount"
        token_str = "dailyKlimaRetirements_token"

        tco2_df = df.loc[
            (df[token_str] == "BCT") |
            (df[token_str] == "NCT")].copy()

        tco2_df = tco2_df.assign(dailyKlimaRetirements_token='TCO2')
        tco2_df = tco2_df.groupby([datetime_str])[amount_str].sum().reset_index()

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

        return ListData(klima_retirements_df)

    def modify_klima_token_retirements_df(self, df):
        df = df.rename(
            columns={
                'klimaRetires_beneficiaryAddress': 'Beneficiary Address',
                'klimaRetires_token': 'Pool',
                'klimaRetires_datetime': 'Date',
                'klimaRetires_proof': 'View on PolygonScan',
                'klimaRetires_amount': 'Amount in Tonnes'})

        df['Amount in Tonnes'] = df['Amount in Tonnes'].apply(lambda x: f'{round(x, 3)}')
        df['View on PolygonScan'] = df[
            'View on PolygonScan'].apply(lambda x: f'[Click Here]({x})')

        return df

    def replace_klima_retirements_token_values(self, df):
        df['Token'] = df['Token'].replace(['BCT'], 'TCO2')
        df['Token'] = df['Token'].replace(['NCT'], 'TCO2')
        df['Token'] = df['Token'].replace(['UBO'], 'C3T')
        df['Token'] = df['Token'].replace(['NBO'], 'C3T')

        return df
