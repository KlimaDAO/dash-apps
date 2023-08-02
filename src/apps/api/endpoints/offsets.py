from flask_restful import Resource, reqparse
from src.apps.services import Offsets as Service, layout_cache
from . import helpers


BRIDGES = ["all", "offchain", "toucan", "c3", "moss", "polygon", "eth"]
POOLS = ["ubo", "nbo", "nct", "bct"]
STATUSES = ["issued", "bridged", "deposited", "redeemed", "retired"]
DATE_FIELDS = [
    "bridged_date",
    "issuance_date",
    "retirement_date",
]
BASE_HELP = f"""Query Parameters
        bridge: one of {BRIDGES}
        pool: one of {POOLS}
        offset_status: one of {STATUSES}
        """

offsets_filter_parser = reqparse.RequestParser()
offsets_filter_parser.add_argument('bridge', type=helpers.validate_list(BRIDGES), default="all")
offsets_filter_parser.add_argument('pool', type=helpers.validate_list(POOLS + [None]), default=None)
offsets_filter_parser.add_argument('status', type=helpers.validate_list(STATUSES + [None]), default=None)


class AbstractOffsets(Resource):

    def get_default_date_field(self):
        # returns the date field appropriate given the selected status
        args = offsets_filter_parser.parse_args()
        bridge = args["bridge"]
        status = args["status"]
        if status is None:
            return "issuance_date" if bridge == "offchain" else "bridged_date"
        else:
            return helpers.STATUS_TO_DATE_COLUMN_MATRIX.get(status)

    def get_offsets(self):
        args = offsets_filter_parser.parse_args()
        bridge = args["bridge"]
        pool = args["pool"]
        status = args["status"]

        # auto select status
        if status is None:
            status = "issued" if bridge == "offchain" else "bridged"

        # Return offsets
        return Service().filter(bridge, pool, status)


class OffsetsRaw(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
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
    def get(self):
        return self.get_offsets()


class OffsetsDatesAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.dates_aggregation_help(DATE_FIELDS)}
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
        return helpers.apply_date_aggregation(
            DATE_FIELDS,
            self.get_offsets(),
            freq,
            self.get_default_date_field()
        )


class OffsetsCountriesAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
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
    @helpers.with_errors_handler
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
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        offsets = self.get_offsets().methodologies_agg().sum("quantity")
        return offsets


class OffsetsVintageAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        {helpers.OUTPUT_FORMATTER_HELP}
        """
    )
    @helpers.with_output_formatter
    def get(self):
        offsets = self.get_offsets().vintage_agg().sum("quantity")
        return offsets


class OffsetsGlobalAggregation(AbstractOffsets):
    @layout_cache.cached(query_string=True)
    @helpers.with_errors_handler
    @helpers.with_help(
        f"""{BASE_HELP}
        """
    )
    def get(self):
        return {
            "quantity": self.get_offsets().sum("quantity")
        }
