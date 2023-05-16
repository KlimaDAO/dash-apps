from src.apps.tco2_dashboard.figures import token_klima_retirement_chart
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_interface \
    import RetirementTrendsInterface
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types \
    import ChartContent, ListData, TopContent
import dash_bootstrap_components as dbc
from dash import html, dcc
import numpy as np


class RetirementTrendsByToken(RetirementTrendsInterface):

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
        return "Retirement Trends By Token"

    def create_top_content(self) -> TopContent:

        # C3T Retired Info
        c3tRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_c3tRetired"].iloc[0]
        )

        c3tKlimaRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_c3tKlimaRetired"].iloc[0]
        )
        c3tklimaRetiredRatio = c3tKlimaRetired / c3tRetired

        # TCO2 Retired Info
        tco2Retired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_tco2Retired"].iloc[0]
        )
        tco2KlimaRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_tco2KlimaRetired"].iloc[0]
        )
        tco2klimaRetiredRatio = tco2KlimaRetired / tco2Retired

        # MCO2 Retired Info
        mco2Retired = float(
            # Note: We are taking MCO2 retirements from ETH
            self.df_carbon_metrics_eth["carbonMetrics_mco2Retired"].iloc[0]
        )
        mco2KlimaRetired = float(
            self.df_carbon_metrics_polygon["carbonMetrics_mco2KlimaRetired"].iloc[0]
        )
        mco2klimaRetiredRatio = mco2KlimaRetired / mco2Retired

        top_content_data = dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "C3T",
                                className="card-title-retirement-trends",
                            ),
                            html.H5(
                                "Total Retirements (Tonnes)",
                                className="card-title-retirement-trends",
                            ),
                            dbc.CardBody(
                                "{:,}".format(int(c3tRetired)),
                                className="card-text-retirement-trends",
                            ),
                            html.H5(
                                "Percentage Retired via KlimaDAO",
                                className="card-title-retirement-trends",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(c3tklimaRetiredRatio),
                                className="card-text-retirement-trends",
                            ),
                        ],
                    ),
                    lg=4,
                    md=12
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            html.H5(
                                "TCO2",
                                className="card-title-retirement-trends",
                            ),
                            html.H5(
                                "Total Retirements (Tonnes)",
                                className="card-title-retirement-trends",
                            ),
                            dbc.CardBody(
                                "{:,}".format(int(tco2Retired)),
                                className="card-text-retirement-trends",
                            ),
                            html.H5(
                                "Percentage Retired via KlimaDAO",
                                className="card-title-retirement-trends",
                            ),
                            dbc.CardBody(
                                "{:.2%}".format(tco2klimaRetiredRatio),
                                className="card-text-retirement-trends",
                            ),
                        ],
                    ),
                    lg=4,
                    md=12
                ),
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
                                "{:.2%}".format(mco2klimaRetiredRatio),
                                className="card-text-retirement-trends",
                            ),
                        ],
                    ),
                    lg=4,
                    md=12
                ),
            ],
        ),

        return TopContent(top_content_data)

    def create_chart_content(self) -> ChartContent:
        tco2_df, c3t_df = self.merge_daily_retirements_df(
            self.agg_daily_klima_retirements)

        mco2_df = self.agg_daily_klima_retirements[
            self.agg_daily_klima_retirements['dailyKlimaRetirements_token']
            == "MCO2"]

        retirement_chart_figure = token_klima_retirement_chart(
            tco2_df,
            mco2_df,
            c3t_df)

        content = dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5("KlimaDAO Retirements by Token",
                                        className="card-title"),
                                dbc.CardBody(
                                    dcc.Graph(figure=retirement_chart_figure)),
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
                'klimaRetires_offset_bridge': 'Bridge',
                'klimaRetires_token': 'Token',
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

        df = self.replace_klima_retirements_token_values(df)

        df['Project_num'] = df['Project'].str.split("-", expand = True)[1]

        df.Project_num.fillna('N/A', inplace=True)

        verra_l = 'https://registry.verra.org/app/projectDetail/VCS/'

        df['Project_Link'] = verra_l

        df["Project_Link"] = df["Project_Link"] + df["Project_num"]

        missing_condition_1 = df['Project_Link'].str.match(
            'https://registry.verra.org/app/projectDetail/VCS/N/A')
        
        df['Project_Link'] = np.where(
             missing_condition_1, "N/A",
            "[" + df['Project'] + "]" + "(" + df['Project_Link'] + ")"
             )
        
        mco2_condition = df['Token'].str.match('MCO2')

        df['Project_Link'] = np.where(mco2_condition, 'N/A', df['Project_Link'])

        df.drop(['Project', 'Project_num', 'Bridge'], axis=1, inplace=True)

        df = df.rename(
              columns={
                    'Project_Link': 'Project'
              }
        )

        df = df[['Beneficiary Address',
                 'Project',
                 'Token',
                 'Date',
                 'Amount in Tonnes',
                 'View on PolygonScan',
                 'Pledge']]


        return df

    def replace_klima_retirements_token_values(self, df):
        df['Token'] = df['Token'].replace(['BCT'], 'TCO2')
        df['Token'] = df['Token'].replace(['NCT'], 'TCO2')
        df['Token'] = df['Token'].replace(['UBO'], 'C3T')
        df['Token'] = df['Token'].replace(['NBO'], 'C3T')

        return df
