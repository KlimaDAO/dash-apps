import pandas as pd
from src.apps.tco2_dashboard.figures import chain_klima_retirement_chart
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_interface \
    import RetirementTrendsInterface
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types \
    import ChartContent, ListData, TopContent
import dash_bootstrap_components as dbc
from dash import html, dcc
from src.apps.services import Offsets, KlimaRetirements, Metrics


class RetirementTrendsByChain(RetirementTrendsInterface):
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

        polygon_on_chain_retirements = Metrics().polygon().latest()[total_ret_string]
        eth_on_chain_retirements = Metrics().eth().latest()[total_ret_string]
        total_on_chain_retirements = \
            polygon_on_chain_retirements + eth_on_chain_retirements

        klima_on_chain_retirements = Metrics().polygon().latest()[total_klima_ret_string]
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
            ),
            lg=6,
            md=12,
        )

    def create_top_right_column(self):
        offchain_quantity = Offsets().filter("offchain", None, "issued").sum("Quantity")
        offchain_retired_quantity = Offsets().filter("offchain", None, "retired").sum("Quantity")
        bridged_quantity = sum(
            Offsets().filter(bridge, None, "bridged").sum("Quantity")
            for bridge in
            ["Toucan", "Moss", "C3"]
        )

        verra_retired = "{:,}".format(int(offchain_retired_quantity))

        verra_perc_retired = "{:.2%}".format(offchain_retired_quantity /
                                             (offchain_quantity - bridged_quantity)
                                             )
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
            ),
            lg=6,
            md=12,
        )

    def create_chart_content(self) -> ChartContent:
        on_chain_df = self.merge_daily_klima_retirements_df(
            KlimaRetirements().daily_agg().resolve())

        off_chain_df = Offsets().filter("offchain", None, "retired").daily_agg("Date").sum("Quantity")
        retirement_chart_figure = chain_klima_retirement_chart(
            on_chain_df,
            off_chain_df)

        content = dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H5(
                                    "Retirements by Chain",
                                    className="card-title"),
                                dbc.CardBody(
                                    dcc.Graph(figure=retirement_chart_figure)),
                                dbc.CardFooter(
                                    "On chain includes only KlimaDAO retirements",
                                    className="card-footer",
                                    style={"paddingTop": "10px"},
                                ),
                            ]
                        )
                    ],
                    width=12,
                ),
            ]
        )
        return ChartContent(content)

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
            KlimaRetirements().raw()
        )

        offchain_retirements = Offsets().filter("offchain", None, "retired").resolve()
        offchain_retirements["Date"] = offchain_retirements["Retirement/Cancellation Date"]
        verra_retirements_df = self.modify_verra_retirements_fg(
            offchain_retirements
        )

        frames = [verra_retirements_df, klima_retirements_df]

        merged = pd.concat(frames)

        return ListData("Detailed list of Retirements", "Date", merged)

    def modify_klima_token_retirements_df(self, df):
        df = df.rename(
            columns={
                'klimaRetires_beneficiaryAddress': 'Beneficiary',
                'klimaRetires_token': 'On/Off Chain',
                'klimaRetires_datetime': 'Date',
                'klimaRetires_proof': 'Proof',
                'klimaRetires_amount': 'Amount in Tonnes'})

        df['Amount in Tonnes'] = df[
            'Amount in Tonnes'].round(3)
        df = df.assign(**{"On/Off Chain": 'On'})
        df['Proof'] = '[Click Here](' + df['Proof'] + ')'
        df['Pledge'] = (
            '[Click Here](https://www.klimadao.finance/pledge/' +
            df['Beneficiary'] + ')'
        )
        df['Date'] = df[
            'Date'].astype(str).str.split(n=1).str[0]

        return df

    def modify_verra_retirements_fg(self, df):
        filtered_df = df[['Retirement Beneficiary',
                          'Credit Type',
                          'Date',
                          'Serial Number',
                          'Quantity']].copy()
        filtered_df = filtered_df.assign(**{"Credit Type": 'Off'})
        filtered_df['Date'] = filtered_df[
            'Date'].astype(str)

        filtered_df = filtered_df.rename(
            columns={
                'Retirement Beneficiary': 'Beneficiary',
                'Credit Type': 'On/Off Chain',
                'Serial Number': 'Proof',
                'Quantity': 'Amount in Tonnes'})

        return filtered_df
