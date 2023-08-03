from flask_restful import Resource, reqparse
from src.apps.services import Pools as Service, layout_cache
from . import helpers


POOLS = ["ubo", "nbo", "nct", "bct"]
STATUSES = ["deposited", "redeemed", "retired"]
OPERATORS = ["sum", "cumsum"]
DATE_FIELDS = [
    "retirement_date",
    "deposited_date",
    "redeemed_date"
]
BASE_HELP = f"""Query Parameters
        pool: one of {POOLS}
        status: one of {STATUSES}
        """

pools_filter_parser = reqparse.RequestParser()
pools_filter_parser.add_argument('pool', type=helpers.validate_list(POOLS + [None]), default=None)
pools_filter_parser.add_argument('status', type=helpers.validate_list(STATUSES + [None]), default="deposited")


class AbstractPools(Resource):
    def get_default_date_field(self):
        # returns the date field appropriate given the selected status
        args = pools_filter_parser.parse_args()
        status = args["status"]
        if status is None:
            return "deposited_date"
        else:
            return helpers.status_date_column(status)

    def get_pool(self):
        args = pools_filter_parser.parse_args()
        pool = args["pool"]
        status = args["status"]

        return Service().filter(pool, status)


class PoolsRaw(AbstractPools):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    @helpers.with_daterange_filter("retirement_date")
    @helpers.with_daterange_filter("deposited_date")
    @helpers.with_daterange_filter("redeemed_date")
    def get(self):
        return self.get_pool()


class PoolsDatesAggregation(AbstractPools):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    @helpers.with_daterange_filter("retirement_date")
    @helpers.with_daterange_filter("deposited_date")
    @helpers.with_daterange_filter("redeemed_date")
    def get(self, freq):
        return helpers.apply_date_aggregation(
            DATE_FIELDS,
            self.get_pool(),
            freq,
            self.get_default_date_field()
        )


class PoolsGlobalAggregation(AbstractPools):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        """
    )
    def get(self):
        return {
            "quantity": self.get_pool().sum("quantity")
        }
