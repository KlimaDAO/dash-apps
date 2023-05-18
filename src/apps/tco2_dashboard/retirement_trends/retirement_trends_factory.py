from src.apps.tco2_dashboard.retirement_trends.impl.retirement_trends_chain \
     import RetirementTrendsByChain
from src.apps.tco2_dashboard.retirement_trends.impl.retirement_trends_pool \
     import RetirementTrendsByPool
from src.apps.tco2_dashboard.retirement_trends.impl.retirement_trends_token \
     import RetirementTrendsByToken
from src.apps.tco2_dashboard.retirement_trends.impl.retirement_trends_beneficiary \
     import RetirementTrendsByBeneficiary
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_interface \
     import RetirementTrendsInterface
from src.apps.tco2_dashboard.retirement_trends.retirement_trends_types \
     import TYPE_CHAIN, TYPE_POOL, TYPE_TOKEN, TYPE_BENEFICIARY


class RetirementTrendsFactory:

    def __init__(
            self,
            retirement_trend_inputs):

        self.retirement_trend_inputs = retirement_trend_inputs

    def get_instance(self, type) -> RetirementTrendsInterface:
        if type == TYPE_POOL:
            return RetirementTrendsByPool(
                self.retirement_trend_inputs
            )

        elif type == TYPE_TOKEN:
            return RetirementTrendsByToken(
                self.retirement_trend_inputs
            )
        elif type == TYPE_CHAIN:
            return RetirementTrendsByChain(
                self.retirement_trend_inputs
            )
        elif type == TYPE_BENEFICIARY:
            return RetirementTrendsByBeneficiary(
                self.retirement_trend_inputs
            )
        else:
            raise KeyError("Wrong type")
