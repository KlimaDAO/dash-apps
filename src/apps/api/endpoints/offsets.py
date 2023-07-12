from flask_restful import Resource, reqparse
from src.apps.services import Offsets as Service, layout_cache
from . import helpers


BRIDGES = ["all", "offchain", "toucan", "c3", "moss", "polygon", "eth"]
POOLS = ["ubo", "nbo", "nct", "bct"]
STATUSES = ["issued", "bridged", "deposited", "redeemed", "retired"]
OPERATORS = ["sum", "cumsum"]
DATE_FIELDS = [
    "bridged_date",
    "issuance_date",
    "retirement_date",
    "deposited_date",
    "redeemed_date"
]
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
offsets_agg_parser.add_argument('date_field', type=helpers.validate_list(DATE_FIELDS), required=True)
offsets_agg_parser.add_argument('operator', type=helpers.validate_list(OPERATORS), default="sum")


class AbstractOffsets(Resource):
    def get_offsets(self):
        args = offsets_filter_parser.parse_args()
        bridge = args["bridge"]
        pool = args["pool"]
        offset_status = args["offset_status"]
        if offset_status is None:
            offset_status = "issued" if bridge == "offchain" else "bridged"

        # Return offsets
        return Service().filter(bridge, pool, offset_status)


class OffsetsRaw(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    @helpers.with_daterange_filter("bridged_date")
    @helpers.with_daterange_filter("issuance_date")
    @helpers.with_daterange_filter("retirement_date")
    @helpers.with_daterange_filter("deposited_date")
    @helpers.with_daterange_filter("redeemed_date")
    def get(self):
        return self.get_offsets()


class OffsetsDatesAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        date_field: Field on which to perform the aggregation. One of {DATE_FIELDS}
        operator: one of {OPERATORS}
        {helpers.OUTPUT_FORMATTER_HELP}
        {helpers.DATES_FILTER_HELP}
        """
    )
    @helpers.with_output_formatter
    @helpers.with_daterange_filter("bridged_date")
    @helpers.with_daterange_filter("issuance_date")
    @helpers.with_daterange_filter("retirement_date")
    @helpers.with_daterange_filter("deposited_date")
    @helpers.with_daterange_filter("redeemed_date")
    def get(self, freq):
        # TODO: fix date comparisons
        args = offsets_agg_parser.parse_args()
        date_column = args["date_field"]
        operator = args["operator"]
        offsets = self.get_offsets()
        if operator == "sum":
            offsets.date_agg(date_column, freq).sum("quantity")
        elif operator == "cumsum":
            offsets.sum_over_time(date_column, "quantity", freq)

        return offsets


class OffsetsCountriesAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        offsets = self.get_offsets().countries_agg().sum("quantity")
        return offsets


class OffsetsProjectsAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        offsets = self.get_offsets().projects_agg().sum("quantity")
        return offsets


class OffsetsMethodologiesAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        offsets = self.get_offsets().methodologies_agg().sum("quantity")
        return offsets


class OffsetsGlobalAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_help(
        f"""{BASE_HELP}
        """
    )
    def get(self):
        return {
            "quantity": self.get_offsets().sum("quantity")
        }
