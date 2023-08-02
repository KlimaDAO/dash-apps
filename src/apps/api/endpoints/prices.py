from flask_restful import Resource, reqparse
from src.apps.services import Prices as Service, services_short_cache, ALL_TOKENS
from . import helpers

parser = reqparse.RequestParser()
parser.add_argument('token', type=helpers.validate_list(ALL_TOKENS))


class Prices(Resource):
    @services_short_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""
        {helpers.OUTPUT_FORMATTER_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    @helpers.with_daterange_filter("date")
    def get(self):
        args = parser.parse_args()
        token = args["token"]
        print(token)
        return Service().filter(token)
