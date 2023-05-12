import numpy as np
import pandas as pd
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_interface \
    import RetirementTrendsInterface
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types \
    import ChartContent, ListData, TopContent


class RetirementTrendsByBeneficiary(RetirementTrendsInterface):

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
        return "Retirement Trends By Beneficiary"

    def create_top_content(self) -> TopContent:
        return None

    def create_chart_content(self) -> ChartContent:
        return None

    def create_list_data(self) -> ListData:
        agg_beneficiary_retirements = self.aggregate_beneficiary_retirements(
            self.raw_klima_retirements
        )

        return ListData("Detailed list of Retirements",
                        "Total Tonnes Retired",
                        agg_beneficiary_retirements)

    def aggregate_beneficiary_retirements(self, df):

        agg_beneficiary_retirements = \
            df.groupby('klimaRetires_beneficiaryAddress').agg(
                {'klimaRetires_amount': ['sum', 'count']}).reset_index()

        agg_beneficiary_retirements = agg_beneficiary_retirements.rename(
            columns={
                'klimaRetires_beneficiaryAddress': 'Beneficiary',
                'count': '# of Retirements',
                'sum': 'Total Tonnes Retired',
            })
   
        agg_beneficiary_retirements['Pledge'] = (
            '[Click Here](https://www.klimadao.finance/pledge/' +
            agg_beneficiary_retirements['Beneficiary'] + ')'
        )

        return agg_beneficiary_retirements
