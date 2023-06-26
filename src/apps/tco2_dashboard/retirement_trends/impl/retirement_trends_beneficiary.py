from src.apps.tco2_dashboard.retirement_trends.retirement_trends_interface \
    import RetirementTrendsInterface
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types \
    import ChartContent, ListData, TopContent
from ...services import KlimaRetirements


class RetirementTrendsByBeneficiary(RetirementTrendsInterface):
    def create_header(self) -> str:
        return "Retirement Trends By Beneficiary"

    def create_top_content(self) -> TopContent:
        return None

    def create_chart_content(self) -> ChartContent:
        return None

    def create_list_data(self) -> ListData:
        agg_beneficiary_retirements = self.aggregate_beneficiary_retirements(
            KlimaRetirements().raw()
        )

        return ListData("Detailed list of Retirements",
                        "Total Tonnes Retired",
                        agg_beneficiary_retirements)

    def aggregate_beneficiary_retirements(self, df):

        agg_beneficiary_retirements = \
            df.groupby('klimaRetires_beneficiaryAddress')[
                'klimaRetires_amount'].agg(['sum', 'count']).reset_index()

        agg_beneficiary_retirements = agg_beneficiary_retirements.rename(
            columns={
                'klimaRetires_beneficiaryAddress': 'Beneficiary',
                'count': '# of Retirements',
                'sum': 'Total Tonnes Retired',
            })

        agg_beneficiary_retirements['Total Tonnes Retired'] = \
            agg_beneficiary_retirements['Total Tonnes Retired'].round(3)

        agg_beneficiary_retirements['Pledge'] = (
            '[Click Here](https://www.klimadao.finance/pledge/' +
            agg_beneficiary_retirements['Beneficiary'] + ')'
        )

        return agg_beneficiary_retirements
