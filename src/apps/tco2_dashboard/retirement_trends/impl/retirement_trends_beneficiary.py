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

        df['klimaRetires_beneficiaryAddress_duplicate'] = \
            df.loc[:, 'klimaRetires_beneficiaryAddress']

        agg_beneficiary_retirements = pd.pivot_table(
            df,
            index=['klimaRetires_beneficiaryAddress'],
            aggfunc={'klimaRetires_amount': np.sum,
                     'klimaRetires_beneficiaryAddress_duplicate': len}
        ).rename(columns={
            'klimaRetires_beneficiaryAddress': 'Beneficiary',
            'klimaRetires_beneficiaryAddress_duplicate': '# of Retirements',
            'klimaRetires_amount': 'Total Tonnes Retired',
        })

        agg_beneficiary_retirements['Pledge'] = (
            '[Click Here](https://www.klimadao.finance/pledge/' +
            df['Beneficiary'] + ')'
        )

        return agg_beneficiary_retirements
