from flask_restful import Resource, reqparse
from src.apps.services import Offsets as Service, services_slow_cache
from . import helpers


BRIDGES = ["all", "offchain", "Toucan", "C3", "Moss", "Polygon", "Eth"]
POOLS = ["UBO", "NBO", "NCT", "BCT"]
STATUSES = ["issued", "bridged", "deposited", "redeemed", "retired"]

parser = reqparse.RequestParser()
parser.add_argument('bridge', type=helpers.validate_list(BRIDGES), default="all")
parser.add_argument('pool', type=helpers.validate_list(POOLS + [None]), default=None)
parser.add_argument('offset_status', type=helpers.validate_list(STATUSES + [None]), default=None)


class OffsetsRaw(Resource):
    @services_slow_cache.cached(query_string=True)
    @helpers.with_help(
        f"""Query Parameters
        bridge: one of {BRIDGES}
        pool: one of {POOLS}
        offset_status: one of {STATUSES}
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
        # Parse arguments
        args = parser.parse_args()
        bridge = args["bridge"]
        pool = args["pool"]
        offset_status = args["offset_status"]
        if offset_status is None:
            offset_status = "issued" if bridge == "offchain" else "bridged"

        # Fetch and slice data
        return Service().filter(bridge, pool, offset_status)
