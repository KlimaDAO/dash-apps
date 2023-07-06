from flask_restful import Resource
from src.apps.services import KlimaRetirements as Service, layout_cache
from . import helpers


class RetirementsRaw(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        retirements = Service()
        return retirements.raw()


class RetirementsDatesAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, freq):
        retirements = Service().get()
        retirements.date_agg(["Date", "Token"], freq).sum("Amount")
        return retirements


class RetirementsBeneficiariesAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        retirements = Service().get()
        retirements.beneficiaries_agg().agg("Amount", {
            "sum": "Amount retired",
            "count": "Number of retirements"
        })
        return retirements


class RetirementsGlobalAggregation(Resource):
    @layout_cache.cached(query_string=True)
    def get(self):
        return {
            "value": Service().get().sum("Amount")
        }
