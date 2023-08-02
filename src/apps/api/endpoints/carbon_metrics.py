from flask_restful import Resource
from src.apps.services import Metrics as Service, layout_cache, DashArgumentException
from . import helpers


class CarbonMetrics(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    @helpers.with_daterange_filter("date")
    def get(self, chain):
        service = Service()
        if (chain not in ["eth", "polygon", "celo", "all"]):
            raise DashArgumentException(f"Unknown chain '{chain}'")
        metrics = getattr(service, chain)()
        return metrics
