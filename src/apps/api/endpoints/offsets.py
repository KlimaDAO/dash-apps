from flask_restful import Resource, reqparse
from src.apps.services import Offsets as Service, services_slow_cache
from . import helpers


BRIDGES = ["all", "offchain", "Toucan", "C3", "Moss", "Polygon", "Eth"]
POOLS = ["UBO", "NBO", "NCT", "BCT"]
STATUSES = ["issued", "bridged", "deposited", "redeemed", "retired"]
OPERATORS = ["sum", "cumsum"]
DATE_FIELDS = {
    "bridged_date": "Bridged Date",
    "issuance_date": "Issuance Date",
    "retirement_date": "Retirement Date",
    "deposit_date": "Deposited Date",
    "redeemed_date": "Redeemed Date"
}
BASE_HELP = f"""Query Parameters
        bridge: one of {BRIDGES}
        pool: one of {POOLS}
        offset_status: one of {STATUSES}
        """

offsets_filter_parser = reqparse.RequestParser()
offsets_filter_parser.add_argument('bridge', type=helpers.validate_list(BRIDGES), default="all")
offsets_filter_parser.add_argument('pool', type=helpers.validate_list(POOLS + [None]), default=None)
offsets_filter_parser.add_argument('offset_status', type=helpers.validate_list(STATUSES + [None]), default=None)

offsets_agg_parser = reqparse.RequestParser()
offsets_agg_parser.add_argument('date_field', type=helpers.validate_list(DATE_FIELDS.keys()), required=True)
offsets_agg_parser.add_argument('operator', type=helpers.validate_list(OPERATORS), default="sum")


class AbstractOffsets(Resource):
    def get_offsets(self):
        args = offsets_filter_parser.parse_args()
        bridge = args["bridge"]
        pool = args["pool"]
        offset_status = args["offset_status"]
        if offset_status is None:
            offset_status = "issued" if bridge == "offchain" else "bridged"

        # Fetch and slice data
        return Service().filter(bridge, pool, offset_status)


class OffsetsRaw(AbstractOffsets):
    @services_slow_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.PAGINATION_HELP}
        """
    )
    @helpers.with_output_formatter
    @helpers.with_daterange_filter("bridged_date", "Bridged Date")
    @helpers.with_daterange_filter("issuance_date", "Issuance Date")
    @helpers.with_daterange_filter("retirement_date", "Retirement Date")
    @helpers.with_daterange_filter("deposit_date", "Deposited Date")
    @helpers.with_daterange_filter("redeemed_date", "Redeemed Date")
    def get(self):
        return self.get_offsets()


class OffsetsDateAggregation(AbstractOffsets):
    @services_slow_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        date_field: Field on which to perform the aggregation. One of {list(DATE_FIELDS.keys())}
        operator: one of {OPERATORS}
        {helpers.PAGINATION_HELP}
        """
    )
    @helpers.with_output_formatter
    @helpers.with_daterange_filter("bridged_date", "Bridged Date")
    @helpers.with_daterange_filter("issuance_date", "Issuance Date")
    @helpers.with_daterange_filter("retirement_date", "Retirement Date")
    @helpers.with_daterange_filter("deposit_date", "Deposited Date")
    @helpers.with_daterange_filter("redeemed_date", "Redeemed Date")
    def get(self, freq):
        args = offsets_agg_parser.parse_args()
        date_column = DATE_FIELDS[args["date_field"]]
        operator = args["operator"]
        offsets = self.get_offsets()
        if operator == "sum":
            offsets.date_agg(date_column, freq).sum("Quantity")
        elif operator == "cumsum":
            offsets.sum_over_time(date_column, "Quantity", freq)

        return offsets


class OffsetsCountriesAggregation(AbstractOffsets):
    @services_slow_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.PAGINATION_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        offsets = self.get_offsets().country_agg().sum("Quantity")
        return offsets


class OffsetsProjectsAggregation(AbstractOffsets):
    @services_slow_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.PAGINATION_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        offsets = self.get_offsets().project_agg().sum("Quantity")
        return offsets


class OffsetsMethodologiesAggregation(AbstractOffsets):
    @services_slow_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.PAGINATION_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        offsets = self.get_offsets().methodology_agg().sum("Quantity")
        return offsets
