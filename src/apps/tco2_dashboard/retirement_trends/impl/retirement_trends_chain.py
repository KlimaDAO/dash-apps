import pandas as pd
from src.apps.tco2_dashboard.figures import chain_klima_retirement_chart
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_interface \
    import RetirementTrendsInterface
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types \
    import ChartData, ListData, TopContent
import dash_bootstrap_components as dbc
from dash import html


class RetirementTrendsByChain(RetirementTrendsInterface):

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

        self.bridges_info_dict = \
            retirement_trend_inputs.bridges_info_dict

        self.df_verra = retirement_trend_inputs.df_verra
        self.df_verra_retired = retirement_trend_inputs.df_verra_retired
        self.no_verra_data = retirement_trend_inputs.verra_fallback_note != ""

    def create_header(self) -> str:
        return "Retirement Trends By Chain"

    def create_top_content(self) -> TopContent:

        top_left_column = self.create_top_left_column()
        top_right_column = self.create_top_right_column()

        top_content_data = [dbc.Row(
            [
                top_left_column,
                top_right_column,
            ]
        )]

        return TopContent(top_content_data)

    def create_top_left_column(self):

        total_ret_string = "carbonMetrics_totalRetirements"
        total_klima_ret_string = "carbonMetrics_totalKlimaRetirements"

        polygon_on_chain_retirements = \
            self.df_carbon_metrics_polygon[total_ret_string].iloc[0]

        eth_on_chain_retirements = \
            self.df_carbon_metrics_eth[total_ret_string].iloc[0]

        total_on_chain_retirements = \
            polygon_on_chain_retirements + eth_on_chain_retirements

        klima_on_chain_retirements = \
            self.df_carbon_metrics_polygon[total_klima_ret_string].iloc[0]

        klima_retirments_ratio = \
            klima_on_chain_retirements / total_on_chain_retirements

        return dbc.Col(
            dbc.Card(
                [
                    html.H5(
                        "On-Chain",
                        className="card-title-retirement-trends",
                    ),
                    html.H5(
                        "Total Retirements (Tonnes)",
                        className="card-title-retirement-trends",
                    ),
                    dbc.CardBody(
                        "{:,}".format(
                            int(total_on_chain_retirements)),
                        className="card-text-retirement-trends",
                    ),
                    html.H5(
                        "Percentage Retired via KlimaDAO",
                        className="card-title-retirement-trends",
                    ),
                    dbc.CardBody(
                        "{:.2%}".format(klima_retirments_ratio),
                        className="card-text-retirement-trends",
                    ),
                ],
                style={"margin-right": "0px",
                       "margin-top": "0px",
                       "margin-bottom": "0px"}
            ),
            lg=6,
            md=12,
        )

    def create_top_right_column(self):
        verra_retired = "Unknown" \
            if self.no_verra_data else "{:,}".format(int(
                self.df_verra_retired["Quantity"].sum()))

        verra_perc_retired = "Unknown" \
            if self.no_verra_data else "{:.2%}".format(self.df_verra_retired[
                "Quantity"].sum() / (self.df_verra["Quantity"].sum()
                                     - sum(d["Dataframe"]["Quantity"].sum()
                                           for d in
                                           self.bridges_info_dict.values())))
        return dbc.Col(
            dbc.Card(
                [
                    html.Div(
                        [
                            html.H5(
                                "Off-Chain",
                                className="card-title-retirement-trends"),
                            html.Div(
                                html.Span(
                                    "info",
                                    className="material-icons-outlined",
                                    style={
                                        "font-size": "20px"},
                                    id="offchain-verra-tooltip",
                                ),
                                className="tooltip-icon-container",
                            ),
                            dbc.Tooltip(
                                "Off-Chain currently includes only Verra retirements",
                                target="offchain-verra-tooltip",
                                className="offchain-verra-tooltip",
                                placement="top",
                                style={
                                    "background-color": "#303030"},
                            ),
                        ],
                        className="card-title-with-tooltip",
                    ),
                    html.H5(
                        "Total Retirements (Tonnes)",
                        className="card-title-retirement-trends",
                    ),
                    dbc.CardBody(
                        verra_retired,
                        className="card-text-retirement-trends",
                    ),
                    html.H5(
                        "Percentage of Retired Credits",
                        className="card-title-retirement-trends",
                    ),
                    dbc.CardBody(
                        verra_perc_retired,
                        className="card-text-retirement-trends",
                    ),
                ],
                style={"margin-left": "0px",
                       "margin-top": "0px",
                       "margin-bottom": "0px"}
            ),
            lg=6,
            md=12,
        )

    def create_chart_data(self) -> ChartData:
        on_chain_df = self.merge_daily_klima_retirements_df(
            self.agg_daily_klima_retirements)

        off_chain_df = None \
            if self.no_verra_data else self.merge_daily_verra_retirements_df(
                self.df_verra_retired)

        retirement_chart_figure = chain_klima_retirement_chart(
            on_chain_df,
            off_chain_df)

        return ChartData("Retirements by Chain", retirement_chart_figure)

    def merge_daily_klima_retirements_df(self, df):

        datetime_str = "dailyKlimaRetirements_datetime"
        amount_str = "dailyKlimaRetirements_amount"

        df = df.assign(dailyKlimaRetirements_token='On Chain')
        df = df.groupby([datetime_str])[
            amount_str].sum().reset_index()

        return df

    def merge_daily_verra_retirements_df(self, df):
        df = df.groupby(["Date"])[
            "Quantity"].sum().reset_index()

        return df

    def create_list_data(self) -> ListData:
        klima_retirements_df = self.modify_klima_token_retirements_df(
            self.raw_klima_retirements
        )

        if self.no_verra_data:
            return ListData(klima_retirements_df)

        verra_retirements_df = self.modify_verra_retirements_fg(
            self.df_verra_retired
        )

        frames = [klima_retirements_df, verra_retirements_df]

        merged = pd.concat(frames)

        return ListData(merged)

    def modify_klima_token_retirements_df(self, df):
        df = df.rename(
            columns={
                'klimaRetires_beneficiaryAddress': 'Retiree',
                'klimaRetires_token': 'On/Off Chain',
                'klimaRetires_datetime': 'Date',
                'klimaRetires_proof': 'Proof',
                'klimaRetires_amount': 'Amount In Tonnes'})

        df['Amount In Tonnes'] = df[
            'Amount In Tonnes'].apply(lambda x: f'{round(x, 3)}')
        df = df.assign(**{"On/Off Chain": 'On'})
        df['Proof'] = df[
            'Proof'].apply(lambda x: f'[Click Here]({x})')
        df['Date'] = df[
            'Date'].apply(lambda x: f'{str(x.split()[0])}')

        return df

    def modify_verra_retirements_fg(self, df):
        filtered_df = df[['Retirement Beneficiary',
                          'Credit Type',
                          'Date',
                          'Serial Number',
                          'Quantity']].copy()
        filtered_df = filtered_df.assign(**{"Credit Type": 'Off'})
        filtered_df['Date'] = filtered_df[
            'Date'].apply(lambda x: f'{str(x)}')

        filtered_df = filtered_df.rename(
            columns={
                'Retirement Beneficiary': 'Retiree',
                'Credit Type': 'On/Off Chain',
                'Serial Number': 'Proof',
                'Quantity': 'Amount In Tonnes'})

        return filtered_df
