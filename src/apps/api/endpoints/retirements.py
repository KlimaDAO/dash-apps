from flask_restful import Resource
from src.apps.services import Retirements as Service, layout_cache
from . import helpers


class RetirementsRaw(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        Returns raw retirements
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, filter):
        return Service().raw(filter)


class RetirementsDatesAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        Aggregates retirements on retirement date
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, filter, freq):
        retirements = Service().get(filter)
        retirements.date_agg(["Retirement Date"], freq).sum("Quantity")
        return retirements


class RetirementsTokensAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        Aggregates Klima retirements on retirement date and token
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, freq):
        retirements = Service().get("klima")
        retirements.date_agg(["Retirement Date", "Token"], freq).sum("Quantity")
        return retirements


class RetirementsBeneficiariesAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        Aggregates retirements on beneficiary
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, filter):
        retirements = Service().get(filter)
        retirements.beneficiaries_agg().agg("Quantity", {
            "sum": "Amount retired",
            "count": "Number of retirements"
        })
        return retirements


class RetirementsGlobalAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        Returns the amount of retirements
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    def get(self, filter):
        return {
            "Quantity": Service().get(filter).sum("Quantity")
        }
