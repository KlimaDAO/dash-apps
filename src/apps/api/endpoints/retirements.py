from flask_restful import Resource
from src.apps.services import Retirements as Service, layout_cache
from . import helpers


def render_aggregation(df):
    return df.agg("quantity", {
            "sum": "amount_retired",
            "count": "number_of_retirements"
        })


class RetirementsRaw(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
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
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        Aggregates retirements on retirement date
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, filter, freq):
        retirements = Service().get(filter).date_agg(["retirement_date"], freq)
        return render_aggregation(retirements)


class RetirementsTokensAndDatesAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        Aggregates Klima retirements on retirement date and token
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, freq):
        retirements = Service().get("klima").date_agg(["retirement_date"], freq).summary()
        return retirements


class RetirementsTokensAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        Aggregates Klima retirements on token
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        retirements = Service().get("klima").tokens_agg()
        return render_aggregation(retirements)


class RetirementsBeneficiariesAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        Aggregates retirements on beneficiary
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self, filter):
        retirements = Service().get(filter).beneficiaries_agg()
        return render_aggregation(retirements)


class RetirementsGlobalAggregation(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        Returns the amount of retirements
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    def get(self, filter):
        return {
            "quantity": Service().get(filter).sum("quantity")
        }
