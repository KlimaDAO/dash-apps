from flask_restful import Resource
from src.apps.services import Prices as Service, services_slow_cache
from . import helpers


class Prices(Resource):
    @services_slow_cache.cached(query_string=True)
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        return Service().dataset()
