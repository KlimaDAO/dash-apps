from flask_restful import Resource
from src.apps.services import Holdings as Service, layout_cache
from . import helpers


class Holders(Resource):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        return Service().get()
