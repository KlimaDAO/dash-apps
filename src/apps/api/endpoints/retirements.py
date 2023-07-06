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


class RetirementsDateAggregation(Resource):
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
